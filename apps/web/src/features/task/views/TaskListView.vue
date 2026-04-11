<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useLogoutMutation } from '@/features/auth/composables/useAuth';
import TaskCard from '@/features/task/components/TaskCard.vue';
import { useDeleteTaskMutation, useTasks } from '@/features/task/composables/useTasks';

const router = useRouter();
const authStore = useAuthStore();
const tasksQuery = useTasks();
const deleteTaskMutation = useDeleteTaskMutation();
const logoutMutation = useLogoutMutation();
const search = ref('');

const filteredTasks = computed(() => {
  const keyword = search.value.trim().toLowerCase();
  const tasks = tasksQuery.data.value?.items ?? [];
  if (!keyword) {
    return tasks;
  }
  return tasks.filter((task) =>
    [task.title, task.subject, task.grade, task.topic].some((value) =>
      value.toLowerCase().includes(keyword),
    ),
  );
});

async function removeTask(taskId: string) {
  if (!window.confirm('确认删除这份教案任务吗？')) {
    return;
  }
  await deleteTaskMutation.mutateAsync(taskId);
}

async function logout() {
  try {
    if (authStore.token) {
      await logoutMutation.mutateAsync();
    }
  } catch {
    // Ignore logout request failures and clear the local session anyway.
  }
  authStore.clearSession();
  await router.push({ name: 'login' });
}
</script>

<template>
  <div class="page-shell">
    <header class="app-header app-card">
      <div>
        <div class="brand">LessonPilot</div>
        <div class="task-meta">欢迎回来，{{ authStore.user?.name }}</div>
      </div>
      <div class="header-actions">
        <button class="button secondary" type="button" @click="router.push({ name: 'task-create' })">
          开始备课
        </button>
        <button class="button ghost" type="button" @click="logout">退出登录</button>
      </div>
    </header>

    <div class="page-stack">
      <section class="app-card" style="padding: 24px">
        <h1 class="page-title">我的备课</h1>
        <p class="subtitle">打开就有结构，AI 负责填肉，你负责确认和调整。</p>

        <label class="field" style="max-width: 320px">
          <span>搜索最近备课</span>
          <input v-model.trim="search" type="text" placeholder="输入标题、学科或课题" />
        </label>
      </section>

      <section v-if="tasksQuery.isLoading.value" class="app-card empty-state">正在加载备课列表...</section>
      <section v-else-if="filteredTasks.length === 0" class="app-card empty-state">
        <h2>你的备课台还是空的</h2>
        <p class="subtitle">创建第一份教案，体验 AI 带来的结构化备课流程。</p>
        <button class="button primary" type="button" @click="router.push({ name: 'task-create' })">
          开始第一次备课
        </button>
      </section>
      <section v-else class="task-grid">
        <TaskCard
          v-for="task in filteredTasks"
          :key="task.id"
          :task="task"
          @open="router.push({ name: 'editor', params: { taskId: task.id } })"
          @delete="removeTask(task.id)"
        />
      </section>
    </div>
  </div>
</template>
