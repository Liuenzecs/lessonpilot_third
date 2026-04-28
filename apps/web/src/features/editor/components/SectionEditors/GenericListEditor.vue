<script setup lang="ts">
/**
 * 通用字符串列表编辑器。
 * 用于教学准备、学习目标、重点难点预测、知识链接等 section。
 * 支持多行文本：Enter 换行，新增项通过底部按钮。
 */
import { computed, nextTick, ref } from 'vue';

import FormulaText from '@/shared/components/FormulaText.vue';
import { containsFormula } from '@/shared/utils/formula';

const props = defineProps<{
  modelValue: string[];
  disabled?: boolean;
  placeholder?: string;
  itemPrefix?: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string[]];
}>();

const list = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

/** 每项 textarea 的模板引用，用于 auto-resize 和新增后聚焦 */
const textareas = ref<HTMLTextAreaElement[]>([]);

function updateItem(index: number, value: string) {
  const next = [...list.value];
  next[index] = value;
  list.value = next;
}

function addItem() {
  list.value = [...list.value, ''];
  nextTick(() => {
    const last = textareas.value[list.value.length - 1];
    last?.focus();
  });
}

function removeItem(index: number) {
  list.value = list.value.filter((_, i) => i !== index);
}

/** Backspace 在空项且光标在开头时，合并到上一项 */
function handleKeydown(e: KeyboardEvent, index: number) {
  if (e.key === 'Backspace' && !list.value[index] && list.value.length > 1) {
    const target = e.target as HTMLTextAreaElement;
    if (target.selectionStart === 0 && target.selectionEnd === 0) {
      e.preventDefault();
      const prev = textareas.value[index - 1];
      removeItem(index);
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

/** 设置 textarea ref 并初始化高度 */
function setTextareaRef(el: unknown, index: number) {
  if (el instanceof HTMLTextAreaElement) {
    textareas.value[index] = el;
    autoResize(el);
  }
}
</script>

<template>
  <div class="generic-list-editor">
    <div v-for="(item, index) in list" :key="index" class="list-item-row">
      <span v-if="itemPrefix" class="item-prefix">{{ itemPrefix }}</span>
      <span class="item-index">{{ index + 1 }}.</span>
      <div class="formula-field">
        <textarea
          :ref="(el) => setTextareaRef(el, index)"
          class="item-input"
          :value="item"
          :disabled="disabled"
          :placeholder="placeholder ?? `第 ${index + 1} 项`"
          rows="1"
          @input="updateItem(index, ($event.target as HTMLTextAreaElement).value); autoResize($event.target)"
          @keydown="handleKeydown($event, index)"
        />
        <FormulaText
          v-if="containsFormula(item)"
          class="formula-preview"
          :text="item"
          preview
        />
      </div>
      <button
        v-if="!disabled && list.length > 1"
        type="button"
        class="item-remove"
        title="删除"
        @click="removeItem(index)"
      >
        &times;
      </button>
    </div>
    <button
      v-if="!disabled"
      type="button"
      class="add-item-btn"
      @click="addItem"
    >
      + 添加
    </button>
  </div>
</template>
