<script setup lang="ts">
/**
 * 教学重难点编辑器（教案）。
 * 包含重点列表和难点列表。
 */
import type { KeyPoints } from '@lessonpilot/shared-types';
import GenericListEditor from './GenericListEditor.vue';

const props = defineProps<{
  modelValue: KeyPoints;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: KeyPoints];
}>();

function updateKeyPoints(items: string[]) {
  emit('update:modelValue', { ...props.modelValue, keyPoints: items });
}

function updateDifficulties(items: string[]) {
  emit('update:modelValue', { ...props.modelValue, difficulties: items });
}
</script>

<template>
  <div class="key-points-editor">
    <div class="subsection">
      <h4 class="subsection-title">重点</h4>
      <GenericListEditor
        :model-value="modelValue.keyPoints"
        :disabled="disabled"
        placeholder="请输入教学重点"
        @update:model-value="updateKeyPoints"
      />
    </div>
    <div class="subsection">
      <h4 class="subsection-title">难点</h4>
      <GenericListEditor
        :model-value="modelValue.difficulties"
        :disabled="disabled"
        placeholder="请输入教学难点"
        @update:model-value="updateDifficulties"
      />
    </div>
  </div>
</template>
