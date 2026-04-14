<script setup lang="ts">
/**
 * 教学过程编辑器（教案）。
 * 表格形式编辑：环节/时长/教师活动/学生活动/设计意图。
 */
import type { TeachingProcessStep } from '@lessonpilot/shared-types';
import { computed } from 'vue';

const props = defineProps<{
  modelValue: TeachingProcessStep[];
  disabled?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: TeachingProcessStep[]];
}>();

const steps = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

function updateStep(index: number, patch: Partial<TeachingProcessStep>) {
  const next = steps.value.map((step, i) =>
    i === index ? { ...step, ...patch } : step,
  );
  steps.value = next;
}

function addStep() {
  steps.value = [
    ...steps.value,
    {
      phase: '',
      duration: 5,
      teacher_activity: '',
      student_activity: '',
      design_intent: '',
    },
  ];
}

function removeStep(index: number) {
  steps.value = steps.value.filter((_, i) => i !== index);
}
</script>

<template>
  <div class="teaching-process-editor">
    <div v-for="(step, index) in steps" :key="index" class="process-step">
      <div class="step-header">
        <div class="step-phase">
          <label class="step-label">环节</label>
          <input
            type="text"
            class="step-input phase-input"
            :value="step.phase"
            :disabled="disabled"
            placeholder="如：导入新课"
            @input="updateStep(index, { phase: ($event.target as HTMLInputElement).value })"
          />
        </div>
        <div class="step-duration">
          <label class="step-label">时长</label>
          <input
            type="number"
            class="step-input duration-input"
            :value="step.duration"
            :disabled="disabled"
            min="1"
            max="45"
            @input="updateStep(index, { duration: Number(($event.target as HTMLInputElement).value) || 5 })"
          />
          <span class="duration-unit">分钟</span>
        </div>
        <button
          v-if="!disabled && steps.length > 1"
          type="button"
          class="step-remove"
          title="删除环节"
          @click="removeStep(index)"
        >
          &times;
        </button>
      </div>
      <div class="step-body">
        <div class="step-field">
          <label class="step-label">教师活动</label>
          <textarea
            class="step-textarea"
            :value="step.teacher_activity"
            :disabled="disabled"
            placeholder="教师在做什么..."
            rows="2"
            @input="updateStep(index, { teacher_activity: ($event.target as HTMLTextAreaElement).value })"
          />
        </div>
        <div class="step-field">
          <label class="step-label">学生活动</label>
          <textarea
            class="step-textarea"
            :value="step.student_activity"
            :disabled="disabled"
            placeholder="学生在做什么..."
            rows="2"
            @input="updateStep(index, { student_activity: ($event.target as HTMLTextAreaElement).value })"
          />
        </div>
        <div class="step-field">
          <label class="step-label">设计意图</label>
          <textarea
            class="step-textarea"
            :value="step.design_intent"
            :disabled="disabled"
            placeholder="为什么这样设计..."
            rows="2"
            @input="updateStep(index, { design_intent: ($event.target as HTMLTextAreaElement).value })"
          />
        </div>
      </div>
    </div>
    <button
      v-if="!disabled"
      type="button"
      class="add-item-btn"
      @click="addStep"
    >
      + 添加环节
    </button>
  </div>
</template>
