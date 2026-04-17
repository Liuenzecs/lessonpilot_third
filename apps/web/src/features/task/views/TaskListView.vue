<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { exportDocx } from '@/features/export/composables/useExport';
import TaskCard from '@/features/task/components/TaskCard.vue';
import { useDeleteTaskMutation, useDuplicateTaskMutation, useTasks } from '@/features/task/composables/useTasks';
import type { TaskRecord } from '@/features/task/types';
import { request } from '@/shared/api/client';
import { getAppErrorState, getErrorDescription } from '@/shared/api/errors';
import StatePanel from '@/shared/components/StatePanel.vue';
import { useToast } from '@/shared/composables/useToast';

import '@/features/task/styles/workspace.css';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();
const tasksQuery = useTasks();
const deleteTaskMutation = useDeleteTaskMutation();
const duplicateTaskMutation = useDuplicateTaskMutation();

const search = ref('');
const subjectFilter = ref('全部');
const sortOrder = ref<'recent' | 'title'>('recent');

const tasks = computed(() => tasksQuery.data.value?.items ?? []);
const workspaceLoading = computed(() => tasksQuery.isLoading.value && !tasksQuery.data.value);
const availableSubjects = computed(() => ['全部', ...new Set(tasks.value.map((task) => task.subject))]);
const hasTasks = computed(() => tasks.value.length > 0);
const workspaceErrorState = computed(() => {
  if (!tasksQuery.error.value || tasks.value.length > 0) {
    return null;
  }

  return getAppErrorState(tasksQuery.error.value, {
    defaultTitle: '备课台暂时打不开',
    defaultDescription: '你可以重试，或者先去帮助中心看看。',
  });
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

function startFirstTask() {
  void router.push({ name: 'task-create' });
}

async function removeTask(taskId: string) {
  if (!window.confirm('确认删除这份教案吗？')) {
    return;
  }

  try {
    await deleteTaskMutation.mutateAsync(taskId);
    toast.success('教案已删除');
  } catch (error) {
    toast.error('删除教案失败', getErrorDescription(error, '请稍后重试。'));
  }
}

async function duplicateTask(task: TaskRecord) {
  try {
    const duplicatedTask = await duplicateTaskMutation.mutateAsync(task.id);
    toast.info('已复制为新教案，正在进入编辑器。');
    await router.push({ name: 'editor', params: { taskId: duplicatedTask.id } });
  } catch (error) {
    toast.error('复制教案失败', getErrorDescription(error, '请稍后重试。'));
  }
}

async function exportTask(task: TaskRecord) {
  try {
    const documentList = await request<{ items: Array<{ id: string }> }>(`/api/v1/documents/?task_id=${task.id}`);
    const documentId = documentList.items[0]?.id;
    if (!documentId) {
      toast.info('当前还没有可导出的教案内容');
      return;
    }
    await exportDocx(documentId, task.title);
    toast.success('Word 文档已开始下载');
  } catch (error) {
    toast.error('导出失败', getErrorDescription(error, '请稍后重试。'));
  }
}
</script>

<template>
  <section class="workspace-page">
    <template v-if="workspaceLoading">
      <div class="workspace-hero-skeleton app-card">
        <div class="workspace-hero-skeleton-copy">
          <div class="workspace-skeleton-chip" />
          <div class="workspace-skeleton-line long" />
          <div class="workspace-skeleton-line medium" />
        </div>
        <div class="workspace-start-skeleton" />
      </div>

      <div class="task-grid">
        <div v-for="index in 4" :key="index" class="task-card-skeleton" />
      </div>
    </template>

    <template v-else>
      <div class="workspace-hero app-card">
        <div class="workspace-hero-copy">
          <p class="page-eyebrow">备课台</p>
          <h1 class="page-title">我的备课</h1>
          <p class="subtitle">打开就是你的备课桌，最近的教案、搜索、复制和导出都在这里完成。</p>
        </div>

        <button class="workspace-start-card" type="button" @click="router.push({ name: 'task-create' })">
          <span class="workspace-start-title">+ 开始备课</span>
          <span class="workspace-start-subtitle">选择学科和主题，快速生成教案</span>
        </button>
      </div>

      <StatePanel
        v-if="workspaceErrorState"
        icon="📚"
        eyebrow="备课台"
        :title="workspaceErrorState.title"
        :description="workspaceErrorState.description"
        tone="error"
      >
        <template #actions>
          <button class="button primary" type="button" @click="tasksQuery.refetch()">重试</button>
          <button class="button ghost" type="button" @click="router.push({ name: 'help' })">去帮助中心</button>
        </template>
      </StatePanel>

      <div
        v-else-if="!hasTasks"
        class="workspace-empty-state app-card"
      >
        <div class="workspace-empty-icon">📘</div>
        <h2>你的备课台还是空的</h2>
        <p>创建第一份教案，开启高效备课。</p>
        <div class="button-row">
          <button class="button primary" type="button" @click="startFirstTask">开始第一次备课</button>
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
            <label class="workspace-search">
              <span>🔍</span>
              <input v-model.trim="search" type="text" placeholder="搜索" />
            </label>

            <label class="workspace-select">
              <span>学科</span>
              <select v-model="subjectFilter">
                <option v-for="subject in availableSubjects" :key="subject" :value="subject">{{ subject }}</option>
              </select>
            </label>

            <label class="workspace-select">
              <span>排序</span>
              <select v-model="sortOrder">
                <option value="recent">最近修改</option>
                <option value="title">标题</option>
              </select>
            </label>
          </div>
        </div>

        <StatePanel
          v-if="filteredTasks.length === 0"
          icon="🔎"
          title="没有找到匹配的教案"
          description="换个关键词、学科或排序方式试试。"
          tone="empty"
          compact
        >
          <template #actions>
            <button class="button ghost" type="button" @click="search = ''; subjectFilter = '全部'; sortOrder = 'recent'">
              清空筛选
            </button>
          </template>
        </StatePanel>

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
    </template>
  </section>
</template>
