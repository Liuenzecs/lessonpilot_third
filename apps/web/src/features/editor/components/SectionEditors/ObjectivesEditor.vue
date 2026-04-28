<script setup lang="ts">
/**
 * 教学目标编辑器（教案）。
 * 每条目标有维度（知识与技能/过程与方法/情感态度与价值观）和内容。
 * 支持多行文本：Enter 换行，新增项通过底部按钮。
 */
import type { TeachingObjective } from '@lessonpilot/shared-types';
import { computed, nextTick, ref } from 'vue';

import FormulaText from '@/shared/components/FormulaText.vue';
import { containsFormula } from '@/shared/utils/formula';

const props = defineProps<{
  modelValue: TeachingObjective[];
  disabled?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: TeachingObjective[]];
}>();

const objectives = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const textareas = ref<HTMLTextAreaElement[]>([]);

const dimensionLabels: Record<string, string> = {
  knowledge: '知识与技能',
  ability: '过程与方法',
  emotion: '情感态度与价值观',
};

function updateObjective(index: number, patch: Partial<TeachingObjective>) {
  const next = objectives.value.map((obj, i) =>
    i === index ? { ...obj, ...patch } : obj,
  );
  objectives.value = next;
}

function addObjective() {
  objectives.value = [
    ...objectives.value,
    { dimension: 'knowledge', content: '' },
  ];
  nextTick(() => {
    const last = textareas.value[objectives.value.length - 1];
    last?.focus();
  });
}

function removeObjective(index: number) {
  objectives.value = objectives.value.filter((_, i) => i !== index);
}

/** Backspace 在空项且光标在开头时，合并到上一项 */
function handleKeydown(e: KeyboardEvent, index: number) {
  if (
    e.key === 'Backspace' &&
    !objectives.value[index].content &&
    objectives.value.length > 1
  ) {
    const target = e.target as HTMLTextAreaElement;
    if (target.selectionStart === 0 && target.selectionEnd === 0) {
      e.preventDefault();
      const prev = textareas.value[index - 1];
      removeObjective(index);
      nextTick(() => {
        prev?.focus();
      });
    }
  }
}

/** 自动调整 textarea 高度 */
function autoResize(el: HTMLTextAreaElement | EventTarget | null) {
  const textarea = el instanceof HTMLTextAreaElement ? el : null;
  if (!textarea) return;
  textarea.style.height = 'auto';
  textarea.style.height = `${textarea.scrollHeight}px`;
}

function setTextareaRef(el: unknown, index: number) {
  if (el instanceof HTMLTextAreaElement) {
    textareas.value[index] = el;
    autoResize(el);
  }
}
</script>

<template>
  <div class="objectives-editor">
    <div v-for="(obj, index) in objectives" :key="index" class="objective-row">
      <select
        class="dimension-select"
        :value="obj.dimension"
        :disabled="disabled"
        @change="updateObjective(index, { dimension: ($event.target as HTMLSelectElement).value as TeachingObjective['dimension'] })"
      >
        <option v-for="(label, key) in dimensionLabels" :key="key" :value="key">
          {{ label }}
        </option>
      </select>
      <div class="formula-field">
        <textarea
          :ref="(el) => setTextareaRef(el, index)"
          class="objective-content"
          :value="obj.content"
          :disabled="disabled"
          placeholder="请输入教学目标内容"
          rows="1"
          @input="updateObjective(index, { content: ($event.target as HTMLTextAreaElement).value }); autoResize($event.target)"
          @keydown="handleKeydown($event, index)"
        />
        <FormulaText
          v-if="containsFormula(obj.content)"
          class="formula-preview"
          :text="obj.content"
          preview
        />
      </div>
      <button
        v-if="!disabled && objectives.length > 1"
        type="button"
        class="item-remove"
        title="删除"
        @click="removeObjective(index)"
      >
        &times;
      </button>
    </div>
    <button
      v-if="!disabled"
      type="button"
      class="add-item-btn"
      @click="addObjective"
    >
      + 添加目标
    </button>
  </div>
</template>
