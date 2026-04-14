<script setup lang="ts">
/**
 * 学案学习流程编辑器。
 * 包含自主学习、合作探究、展示提升三个子 section，每个是 AssessmentItem 数组。
 */
import type { LearningProcess } from '@lessonpilot/shared-types';
import AssessmentEditor from './AssessmentEditor.vue';

const props = defineProps<{
  modelValue: LearningProcess;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: LearningProcess];
}>();

function updateSelfStudy(items: LearningProcess['selfStudy']) {
  emit('update:modelValue', { ...props.modelValue, selfStudy: items });
}

function updateCollaboration(items: LearningProcess['collaboration']) {
  emit('update:modelValue', { ...props.modelValue, collaboration: items });
}

function updatePresentation(items: LearningProcess['presentation']) {
  emit('update:modelValue', { ...props.modelValue, presentation: items });
}
</script>

<template>
  <div class="learning-process-editor">
    <div class="subsection">
      <h4 class="subsection-title">自主学习</h4>
      <AssessmentEditor
        :model-value="modelValue.selfStudy"
        :disabled="disabled"
        @update:model-value="updateSelfStudy"
      />
    </div>
    <div class="subsection">
      <h4 class="subsection-title">合作探究</h4>
      <AssessmentEditor
        :model-value="modelValue.collaboration"
        :disabled="disabled"
        @update:model-value="updateCollaboration"
      />
    </div>
    <div class="subsection">
      <h4 class="subsection-title">展示提升</h4>
      <AssessmentEditor
        :model-value="modelValue.presentation"
        :disabled="disabled"
        @update:model-value="updatePresentation"
      />
    </div>
  </div>
</template>
