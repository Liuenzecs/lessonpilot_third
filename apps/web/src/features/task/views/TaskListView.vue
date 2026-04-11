<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
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
const accountMenuOpen = ref(false);
const accountMenuRef = ref<HTMLElement | null>(null);

const tasks = computed(() => tasksQuery.data.value?.items ?? []);
const filteredTasks = computed(() => {
  const keyword = search.value.trim().toLowerCase();
  if (!keyword) {
    return tasks.value;
  }

  return tasks.value.filter((task) =>
    [task.title, task.subject, task.grade, task.topic].some((value) =>
      value.toLowerCase().includes(keyword),
    ),
  );
});

const userName = computed(() => authStore.user?.name?.trim() || '老师');
const userInitial = computed(() => userName.value.slice(0, 1).toUpperCase());
const hasTasks = computed(() => tasks.value.length > 0);
const isSearching = computed(() => search.value.trim().length > 0);

function handleGlobalClick(event: MouseEvent) {
  if (!accountMenuRef.value) {
    return;
  }
  if (!accountMenuRef.value.contains(event.target as Node)) {
    accountMenuOpen.value = false;
  }
}

async function removeTask(taskId: string) {
  if (!window.confirm('确认删除这份备课任务吗？')) {
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
    // Ignore logout failures and clear the local session anyway.
  }

  authStore.clearSession();
  accountMenuOpen.value = false;
  await router.push({ name: 'login' });
}

onMounted(() => {
  document.addEventListener('click', handleGlobalClick);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleGlobalClick);
});
</script>

<template>
  <div class="page-shell workspace-page">
    <header class="workspace-topbar">
      <div class="brand">LessonPilot</div>

      <div ref="accountMenuRef" class="workspace-account">
        <button class="workspace-account-trigger" type="button" @click="accountMenuOpen = !accountMenuOpen">
          <span class="workspace-account-avatar">{{ userInitial }}</span>
          <span class="workspace-account-name">{{ userName }}</span>
          <span class="workspace-account-caret">▾</span>
        </button>

        <div v-if="accountMenuOpen" class="workspace-account-menu app-card">
          <div class="workspace-account-menu-label">当前账户</div>
          <div class="workspace-account-menu-name">{{ userName }}</div>
          <button class="workspace-account-menu-item" type="button" @click="logout">
            退出登录
          </button>
        </div>
      </div>
    </header>

    <main class="workspace-stack">
      <section class="workspace-hero app-card">
        <div class="workspace-hero-copy">
          <div class="workspace-hero-badge">AI 备课工作台</div>
          <h1 class="workspace-hero-title">今晚要备的课，打开就能开始。</h1>
          <p class="workspace-hero-text">
            选择学科和主题，先给你清晰骨架，再由 AI 逐段补充内容。老师只需要确认、调整、导出。
          </p>
        </div>

        <button class="workspace-hero-cta" type="button" @click="router.push({ name: 'task-create' })">
          <span class="workspace-hero-cta-title">+ 开始备课</span>
          <span class="workspace-hero-cta-subtitle">选择学科和主题，AI 帮你快速生成</span>
        </button>
      </section>

      <section class="workspace-section">
        <div class="workspace-section-head">
          <div>
            <h2 class="workspace-section-title">最近备课</h2>
            <p class="workspace-section-subtitle">点击卡片直接回到编辑器，不再多一层详情页。</p>
          </div>

          <label class="workspace-search">
            <span class="workspace-search-icon">搜索</span>
            <input v-model.trim="search" type="text" placeholder="按标题、学科或年级筛选" />
          </label>
        </div>

        <div v-if="tasksQuery.isLoading.value" class="workspace-loading-grid">
          <div v-for="index in 3" :key="index" class="workspace-task-skeleton app-card" />
        </div>

        <div v-else-if="!hasTasks" class="workspace-empty app-card">
          <div class="workspace-empty-eyebrow">欢迎来到 LessonPilot</div>
          <h3 class="workspace-empty-title">你的工作台还是空的。</h3>
          <p class="workspace-empty-text">
            点击下方按钮开始第一次备课，3 步完成创建，生成进度会直接在编辑器里展示。
          </p>
          <button class="button primary" type="button" @click="router.push({ name: 'task-create' })">
            开始第一次备课
          </button>
        </div>

        <div v-else-if="filteredTasks.length === 0" class="workspace-empty app-card">
          <div class="workspace-empty-eyebrow">没有找到匹配结果</div>
          <h3 class="workspace-empty-title">换一个关键词试试。</h3>
          <p class="workspace-empty-text">当前搜索词是“{{ search }}”，你也可以直接开始新的备课任务。</p>
          <div class="button-row">
            <button class="button ghost" type="button" @click="search = ''">清空搜索</button>
            <button class="button primary" type="button" @click="router.push({ name: 'task-create' })">
              开始备课
            </button>
          </div>
        </div>

        <div v-else class="workspace-task-grid" :class="{ searching: isSearching }">
          <TaskCard
            v-for="task in filteredTasks"
            :key="task.id"
            :task="task"
            @open="router.push({ name: 'editor', params: { taskId: task.id } })"
            @delete="removeTask(task.id)"
          />
        </div>
      </section>
    </main>
  </div>
</template>
