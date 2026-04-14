<script setup lang="ts">
/**
 * 教学目标编辑器（教案）。
 * 每条目标有维度（知识与技能/过程与方法/情感态度与价值观）和内容。
 */
import type { TeachingObjective } from '@lessonpilot/shared-types';
import { computed } from 'vue';

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
}

function removeObjective(index: number) {
  objectives.value = objectives.value.filter((_, i) => i !== index);
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
      <input
        type="text"
        class="objective-content"
        :value="obj.content"
        :disabled="disabled"
        placeholder="请输入教学目标内容"
        @input="updateObjective(index, { content: ($event.target as HTMLInputElement).value })"
      />
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
