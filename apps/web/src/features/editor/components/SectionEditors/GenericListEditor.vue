<script setup lang="ts">
/**
 * 通用字符串列表编辑器。
 * 用于教学准备、学习目标、重点难点预测、知识链接等 section。
 */
import { computed } from 'vue';

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

function updateItem(index: number, value: string) {
  const next = [...list.value];
  next[index] = value;
  list.value = next;
}

function addItem() {
  list.value = [...list.value, ''];
}

function removeItem(index: number) {
  list.value = list.value.filter((_, i) => i !== index);
}

function handleKeydown(e: KeyboardEvent, index: number) {
  if (e.key === 'Enter') {
    e.preventDefault();
    const next = [...list.value];
    next.splice(index + 1, 0, '');
    list.value = next;
  }
  if (e.key === 'Backspace' && !list.value[index] && list.value.length > 1) {
    e.preventDefault();
    removeItem(index);
  }
}
</script>

<template>
  <div class="generic-list-editor">
    <div v-for="(item, index) in list" :key="index" class="list-item-row">
      <span v-if="itemPrefix" class="item-prefix">{{ itemPrefix }}</span>
      <span class="item-index">{{ index + 1 }}.</span>
      <input
        type="text"
        class="item-input"
        :value="item"
        :disabled="disabled"
        :placeholder="placeholder ?? `第 ${index + 1} 项`"
        @input="updateItem(index, ($event.target as HTMLInputElement).value)"
        @keydown="handleKeydown($event, index)"
      />
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
