<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import { exportDocx } from '@/features/export/composables/useExport';
import TaskCard from '@/features/task/components/TaskCard.vue';
import { useDeleteTaskMutation, useDuplicateTaskMutation, useTasks } from '@/features/task/composables/useTasks';
import { FIRST_LESSON_PRESET_QUERY } from '@/features/task/data/firstLessonPresets';
import type { TaskRecord } from '@/features/task/types';
import { request } from '@/shared/api/client';
import { getAppErrorState, getErrorDescription } from '@/shared/api/errors';
import StatePanel from '@/shared/components/StatePanel.vue';
import { useToast } from '@/shared/composables/useToast';

import '@/features/task/styles/workspace.css';

const router = useRouter();
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

function startSampleTask() {
  void router.push({ name: 'task-create', query: { preset: FIRST_LESSON_PRESET_QUERY } });
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
      <div class="workspace-hero">
        <div class="workspace-hero-copy">
          <p class="page-eyebrow">备课队列</p>
          <h1 class="page-title">今天要处理的备课</h1>
          <p class="subtitle">从这里开始新备课、导入旧教案、管理学校格式，也能快速判断每份文档下一步该做什么。</p>
        </div>

        <div class="workspace-hero-actions">
          <button class="workspace-start-card" type="button" @click="startSampleTask">
            <span class="workspace-start-title">用样例体验</span>
            <span class="workspace-start-subtitle">自动填好《春》第一课时，快速跑通生成、体检和导出</span>
          </button>
          <button class="workspace-start-card secondary" type="button" @click="router.push({ name: 'task-create' })">
            <span class="workspace-start-title">从课题开始</span>
            <span class="workspace-start-subtitle">输入自己的课题，直接进入文档桌起草</span>
          </button>
          <button class="workspace-start-card secondary" type="button" @click="router.push({ name: 'task-import' })">
            <span class="workspace-start-title">导入旧教案</span>
            <span class="workspace-start-subtitle">上传 Word，先预览结构再进入编辑器</span>
          </button>
          <button class="workspace-start-card secondary" type="button" @click="router.push({ name: 'school-templates' })">
            <span class="workspace-start-title">学校格式库</span>
            <span class="workspace-start-subtitle">保存常用 Word 格式，导出时直接套用</span>
          </button>
          <button class="workspace-start-card secondary" type="button" @click="router.push({ name: 'personal-assets' })">
            <span class="workspace-start-title">个人资料柜</span>
            <span class="workspace-start-subtitle">迁移旧讲义和 PPT，沉淀私有资料</span>
          </button>
        </div>
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
        <p>可以先用样例跑完整链路，也可以从自己的课题或旧教案开始。</p>
        <div class="workspace-first-path">
          <span>1. 填好课题</span>
          <span>2. 生成初稿</span>
          <span>3. 体检风险</span>
          <span>4. 导出 Word</span>
        </div>
        <div class="button-row">
          <button class="button primary" type="button" @click="startSampleTask">用样例体验</button>
          <button class="button secondary" type="button" @click="startFirstTask">从课题开始</button>
          <button class="button secondary" type="button" @click="router.push({ name: 'task-import' })">
            导入旧教案
          </button>
          <button class="button ghost" type="button" @click="router.push({ name: 'help' })">
            3 分钟快速上手指南
          </button>
        </div>
      </div>

      <template v-else>
        <div class="workspace-toolbar">
          <div>
            <h2>最近备课队列</h2>
            <p class="subtitle">每一行都是一份可继续处理的备课文档。</p>
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
