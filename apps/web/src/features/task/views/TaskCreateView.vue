<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

import { SUBJECT_OPTIONS, GRADE_OPTIONS } from '@/shared/constants/options';
import { useCreateTaskMutation } from '@/features/task/composables/useTasks';
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
      requirements: form.requirements || null,
    });
    await router.push({ name: 'editor', params: { taskId: task.id } });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      submitError.value = '登录状态已失效，正在返回登录页，请重新登录后再试。';
      return;
    }
    submitError.value = '创建备课任务失败，请稍后重试。';
  }
}
</script>

<template>
  <div class="page-shell">
    <div class="wizard-card app-card">
      <p class="muted">步骤 {{ step }}/3</p>
      <h1 class="page-title">开始新的备课任务</h1>
      <p class="subtitle">每次只做一个选择，让老师在 10 秒内完成创建。</p>

      <template v-if="step === 1">
        <h2>选择学科</h2>
        <div class="selection-grid">
          <button
            v-for="subject in SUBJECT_OPTIONS"
            :key="subject"
            class="selection-card"
            :class="{ active: form.subject === subject }"
            type="button"
            @click="form.subject = subject"
          >
            {{ subject }}
          </button>
        </div>
      </template>

      <template v-else-if="step === 2">
        <h2>选择年级</h2>
        <div class="selection-grid">
          <button
            v-for="grade in GRADE_OPTIONS"
            :key="grade"
            class="selection-card"
            :class="{ active: form.grade === grade }"
            type="button"
            @click="form.grade = grade"
          >
            {{ grade }}
          </button>
        </div>
      </template>

      <template v-else>
        <h2>输入课题主题</h2>
        <label class="field">
          <span>课题</span>
          <input v-model.trim="form.topic" type="text" placeholder="例如：一元二次方程" />
        </label>
        <label class="field">
          <span>补充要求（可选）</span>
          <textarea
            v-model.trim="form.requirements"
            placeholder="例如：重点讲解配方法，控制在 40 分钟课堂节奏内"
          />
        </label>
      </template>

      <div v-if="submitError" class="feedback">{{ submitError }}</div>

      <div class="button-row" style="margin-top: 24px">
        <button class="button ghost" type="button" @click="router.push({ name: 'tasks' })">
          返回备课台
        </button>
        <button class="button secondary" type="button" :disabled="step === 1" @click="step -= 1">
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
          {{ createTaskMutation.isPending.value ? '创建中...' : '生成教案' }}
        </button>
      </div>
    </div>
  </div>
</template>
