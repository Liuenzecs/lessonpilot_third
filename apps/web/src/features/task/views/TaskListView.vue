<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useBillingDialogStore } from '@/app/stores/billing';
import { getBillingErrorDetail } from '@/features/billing/utils';
import { exportDocx } from '@/features/export/composables/useExport';
import { useSubscription } from '@/features/settings/composables/useAccount';
import { useDeleteTaskMutation, useDuplicateTaskMutation, useTasks } from '@/features/task/composables/useTasks';
import TaskCard from '@/features/task/components/TaskCard.vue';
import type { TaskRecord } from '@/features/task/types';
import { request } from '@/shared/api/client';

import '@/features/task/styles/workspace.css';

const router = useRouter();
const billingDialog = useBillingDialogStore();
const tasksQuery = useTasks();
const subscriptionQuery = useSubscription();
const deleteTaskMutation = useDeleteTaskMutation();
const duplicateTaskMutation = useDuplicateTaskMutation();

const search = ref('');
const subjectFilter = ref('全部');
const sortOrder = ref<'recent' | 'title'>('recent');

const tasks = computed(() => tasksQuery.data.value?.items ?? []);
const subscription = computed(() => subscriptionQuery.data.value);
const availableSubjects = computed(() => ['全部', ...new Set(tasks.value.map((task) => task.subject))]);
const hasTasks = computed(() => tasks.value.length > 0);
const subscriptionLabel = computed(() => {
  if (!subscription.value) {
    return '';
  }
  if (subscription.value.status === 'active' || subscription.value.status === 'trialing') {
    return `${subscription.value.plan_label} · 不限量备课已解锁`;
  }
  return `免费版 · 本月剩余 ${subscription.value.quota_remaining ?? 0} / ${subscription.value.monthly_task_limit ?? 5}`;
});

const filteredTasks = computed(() => {
  const keyword = search.value.trim().toLowerCase();
  const filtered = tasks.value.filter((task) => {
    const matchesKeyword =
      !keyword ||
      [task.title, task.subject, task.grade, task.topic].some((value) =>
        value.toLowerCase().includes(keyword),
      );
    const matchesSubject = subjectFilter.value === '全部' || task.subject === subjectFilter.value;
    return matchesKeyword && matchesSubject;
  });

  return [...filtered].sort((left, right) => {
    if (sortOrder.value === 'title') {
      return left.title.localeCompare(right.title, 'zh-CN');
    }
    return new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime();
  });
});

async function removeTask(taskId: string) {
  if (!window.confirm('确认删除这份教案吗？')) {
    return;
  }
  await deleteTaskMutation.mutateAsync(taskId);
}

async function duplicateTask(task: TaskRecord) {
  try {
    const duplicatedTask = await duplicateTaskMutation.mutateAsync(task.id);
    await router.push({ name: 'editor', params: { taskId: duplicatedTask.id } });
  } catch (error) {
    const billingError = getBillingErrorDetail(error);
    if (billingError?.code === 'quota_exceeded') {
      billingDialog.openDialog({
        reason: 'quota_exceeded',
        title: '复制会占用新的教案额度',
        description: billingError.message,
      });
    }
  }
}

async function exportTask(task: TaskRecord) {
  const documentList = await request<{ items: Array<{ id: string }> }>(`/api/v1/documents/?task_id=${task.id}`);
  const documentId = documentList.items[0]?.id;
  if (!documentId) {
    return;
  }
  await exportDocx(documentId, task.title);
}
</script>

<template>
  <section class="workspace-page">
    <div class="workspace-hero app-card">
      <div class="workspace-hero-copy">
        <p class="page-eyebrow">备课台</p>
        <h1 class="page-title">我的备课</h1>
        <p class="subtitle">打开就是你的备课桌，最近的教案、搜索、复制和导出都在这里完成。</p>
        <p v-if="subscriptionLabel" class="subscription-pill">{{ subscriptionLabel }}</p>
      </div>

      <button class="workspace-start-card" type="button" @click="router.push({ name: 'task-create' })">
        <span class="workspace-start-title">+ 开始备课</span>
        <span class="workspace-start-subtitle">选择学科和主题，AI 帮你快速生成</span>
      </button>
    </div>

    <div v-if="!hasTasks && !tasksQuery.isLoading.value" class="workspace-empty-state app-card">
      <div class="workspace-empty-icon">📘</div>
      <h2>你的备课台还是空的</h2>
      <p>创建第一份教案，体验 AI 备课。</p>
      <div class="button-row">
        <button class="button primary" type="button" @click="router.push({ name: 'task-create' })">
          开始第一次备课
        </button>
        <button class="button ghost" type="button" @click="router.push({ name: 'help' })">
          3 分钟快速上手指南
        </button>
      </div>
    </div>

    <template v-else>
      <div class="workspace-toolbar">
        <div>
          <h2>最近备课</h2>
          <p class="subtitle">卡片点击直接进入编辑器，不再多一层详情页。</p>
        </div>

        <div class="workspace-filters">
          <label class="workspace-search app-card">
            <span>🔍</span>
            <input v-model.trim="search" type="text" placeholder="搜索" />
          </label>

          <label class="workspace-select app-card">
            <span>学科</span>
            <select v-model="subjectFilter">
              <option v-for="subject in availableSubjects" :key="subject" :value="subject">{{ subject }}</option>
            </select>
          </label>

          <label class="workspace-select app-card">
            <span>排序</span>
            <select v-model="sortOrder">
              <option value="recent">最近修改</option>
              <option value="title">标题</option>
            </select>
          </label>
        </div>
      </div>

      <div v-if="tasksQuery.isLoading.value" class="task-grid">
        <div v-for="index in 4" :key="index" class="task-card-skeleton app-card" />
      </div>

      <div v-else-if="filteredTasks.length === 0" class="workspace-empty-state app-card compact">
        <h2>没有找到匹配的教案</h2>
        <p>换个关键词、学科或排序方式试试。</p>
      </div>

      <div v-else class="task-grid">
        <TaskCard
          v-for="task in filteredTasks"
          :key="task.id"
          :task="task"
          @open="router.push({ name: 'editor', params: { taskId: task.id } })"
          @export="exportTask(task)"
          @duplicate="duplicateTask(task)"
          @delete="removeTask(task.id)"
        />
      </div>
    </template>
  </section>
</template>
