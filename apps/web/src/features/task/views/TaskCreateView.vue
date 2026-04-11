<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useCreateTaskMutation } from '@/features/task/composables/useTasks';
import { SUBJECT_OPTIONS, GRADE_OPTIONS } from '@/shared/constants/options';
import { ApiError } from '@/shared/api/client';

const router = useRouter();
const createTaskMutation = useCreateTaskMutation();

const step = ref(1);
const submitError = ref('');
const form = reactive({
  subject: '',
  grade: '',
  topic: '',
  requirements: '',
});

const stepMeta = computed(() => {
  if (step.value === 1) {
    return {
      title: '选择学科',
      description: '先选这节课属于哪个学科。',
    };
  }
  if (step.value === 2) {
    return {
      title: '选择年级',
      description: '再告诉 LessonPilot 这节课面向哪个年级。',
    };
  }
  return {
    title: '输入课题主题',
    description: '最后写下课题主题，可再补一句具体要求。',
  };
});

const canGoNext = computed(() => {
  if (step.value === 1) {
    return Boolean(form.subject);
  }
  if (step.value === 2) {
    return Boolean(form.grade);
  }
  return Boolean(form.topic.trim());
});

async function submit() {
  submitError.value = '';

  try {
    const task = await createTaskMutation.mutateAsync({
      ...form,
      requirements: form.requirements.trim() || null,
    });
    await router.push({ name: 'editor', params: { taskId: task.id } });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      submitError.value = '登录状态已失效，请重新登录后再试。';
      return;
    }
    submitError.value = '创建备课任务失败，请稍后重试。';
  }
}
</script>

<template>
  <div class="page-shell wizard-page">
    <div class="wizard-frame app-card">
      <div class="wizard-head">
        <button class="button ghost" type="button" @click="router.push({ name: 'tasks' })">
          返回工作台
        </button>

        <div class="wizard-progress">
          <div class="wizard-progress-label">步骤 {{ step }}/3</div>
          <div class="wizard-progress-dots">
            <span v-for="index in 3" :key="index" class="wizard-progress-dot" :class="{ active: index <= step }" />
          </div>
        </div>
      </div>

      <section class="wizard-content">
        <div class="wizard-copy">
          <div class="wizard-eyebrow">创建向导</div>
          <h1 class="page-title wizard-title">{{ stepMeta.title }}</h1>
          <p class="subtitle wizard-subtitle">{{ stepMeta.description }}</p>
        </div>

        <div v-if="step === 1" class="wizard-choice-grid">
          <button
            v-for="subject in SUBJECT_OPTIONS"
            :key="subject"
            class="wizard-choice-card"
            :class="{ active: form.subject === subject }"
            type="button"
            @click="form.subject = subject"
          >
            {{ subject }}
          </button>
        </div>

        <div v-else-if="step === 2" class="wizard-choice-grid">
          <button
            v-for="grade in GRADE_OPTIONS"
            :key="grade"
            class="wizard-choice-card"
            :class="{ active: form.grade === grade }"
            type="button"
            @click="form.grade = grade"
          >
            {{ grade }}
          </button>
        </div>

        <div v-else class="wizard-form">
          <label class="wizard-field">
            <span class="wizard-field-label">课题主题</span>
            <input
              v-model.trim="form.topic"
              class="wizard-topic-input"
              type="text"
              placeholder="例如：一元二次方程"
            />
          </label>

          <label class="wizard-field">
            <span class="wizard-field-label">补充说明（可选）</span>
            <textarea
              v-model.trim="form.requirements"
              class="wizard-requirements-input"
              placeholder="例如：重点讲解配方法，练习部分增加一道分层题。"
            />
          </label>
        </div>

        <p v-if="submitError" class="feedback">{{ submitError }}</p>
      </section>

      <footer class="wizard-foot">
        <button class="button ghost" type="button" :disabled="step === 1" @click="step -= 1">
          上一步
        </button>

        <button
          v-if="step < 3"
          class="button primary"
          type="button"
          :disabled="!canGoNext"
          @click="step += 1"
        >
          下一步
        </button>

        <button
          v-else
          class="button primary"
          type="button"
          :disabled="!canGoNext || createTaskMutation.isPending.value"
          @click="submit"
        >
          {{ createTaskMutation.isPending.value ? '正在进入编辑器...' : '生成教案' }}
        </button>
      </footer>
    </div>
  </div>
</template>
