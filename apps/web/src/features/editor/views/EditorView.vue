<script setup lang="ts">
import type { Block, ContentDocument, SectionBlock } from '@lessonpilot/shared-types';

import { computed, nextTick, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import BlockRenderer from '@/features/editor/components/BlockRenderer.vue';
import PendingBlockCard from '@/features/editor/components/PendingBlockCard.vue';
import { useTaskDocuments, useUpdateDocumentMutation } from '@/features/editor/composables/useEditor';
import type { LessonDocument } from '@/features/editor/types';
import { exportDocx } from '@/features/export/composables/useExport';
import { consumeGenerationStream } from '@/features/generation/composables/useGeneration';
import { useStartGenerationMutation, useTask } from '@/features/task/composables/useTasks';
import {
  acceptPendingBlock,
  addListBlock,
  addParagraphBlock,
  cloneContent,
  cloneSerializable,
  collectSections,
  findSection,
  getConfirmedChildren,
  getPendingChildren,
  rejectPendingBlock,
} from '@/shared/utils/content';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const taskId = computed(() => String(route.params.taskId ?? ''));
const taskQuery = useTask(taskId.value);
const documentsQuery = useTaskDocuments(taskId.value);
const startGenerationMutation = useStartGenerationMutation(taskId.value);
const draftDocument = ref<LessonDocument | null>(null);
const saveState = ref<'saved' | 'dirty' | 'saving' | 'conflict'>('saved');
const streamError = ref('');
const initialGenerationTriggered = ref(false);
const suppressAutosave = ref(false);
const activeSectionId = ref<string | null>(null);
const generationProgress = reactive({
  isGenerating: false,
  completed: 0,
  total: 0,
  currentSection: '',
});

let saveTimer: number | undefined;

const primaryDocument = computed(() => documentsQuery.data.value?.items[0] ?? null);
const sections = computed(() => (draftDocument.value ? collectSections(draftDocument.value.content) : []));
const updateDocumentMutation = useUpdateDocumentMutation(
  () => draftDocument.value?.id ?? '',
  () => taskId.value,
);

watch(
  primaryDocument,
  (document) => {
    if (!document) {
      return;
    }
    if (!draftDocument.value || saveState.value === 'saved') {
      applyServerDocument(document);
    }
  },
  { immediate: true },
);

watch(
  [taskQuery.data, primaryDocument],
  ([task, document]) => {
    if (!task || !document || initialGenerationTriggered.value) {
      return;
    }
    const hasGeneratedContent = collectSections(document.content).some(
      (section) => section.children.length > 0,
    );
    if (task.status === 'draft' && !hasGeneratedContent) {
      initialGenerationTriggered.value = true;
      void startGeneration();
    }
  },
  { immediate: true },
);

watch(
  () => draftDocument.value?.content,
  () => {
    if (!draftDocument.value || suppressAutosave.value) {
      return;
    }
    saveState.value = 'dirty';
    streamError.value = '';
    if (saveTimer) {
      window.clearTimeout(saveTimer);
    }
    saveTimer = window.setTimeout(() => {
      void persistDocument();
    }, 700);
  },
  { deep: true },
);

function applyServerDocument(document: LessonDocument) {
  suppressAutosave.value = true;
  draftDocument.value = cloneSerializable(document);
  saveState.value = 'saved';
  nextTick(() => {
    suppressAutosave.value = false;
  });
}

async function persistDocument() {
  if (!draftDocument.value) {
    return;
  }

  saveState.value = 'saving';
  try {
    const updatedDocument = await updateDocumentMutation.mutateAsync({
      version: draftDocument.value.version,
      content: draftDocument.value.content,
    });
    applyServerDocument(updatedDocument);
  } catch {
    saveState.value = 'conflict';
  }
}

function updateContent(nextContent: ContentDocument) {
  if (!draftDocument.value) {
    return;
  }
  draftDocument.value = {
    ...draftDocument.value,
    content: cloneContent(nextContent),
  };
}

function updateSectionChild(sectionId: string, childIndex: number, block: Block) {
  if (!draftDocument.value) {
    return;
  }
  const nextContent = cloneContent(draftDocument.value.content);
  const section = findSection(nextContent, sectionId);
  if (!section) {
    return;
  }
  section.children.splice(childIndex, 1, block);
  updateContent(nextContent);
}

function appendParagraph(sectionId: string) {
  if (!draftDocument.value) {
    return;
  }
  const nextContent = cloneContent(draftDocument.value.content);
  const section = findSection(nextContent, sectionId);
  if (!section) {
    return;
  }
  addParagraphBlock(section);
  updateContent(nextContent);
}

function appendList(sectionId: string) {
  if (!draftDocument.value) {
    return;
  }
  const nextContent = cloneContent(draftDocument.value.content);
  const section = findSection(nextContent, sectionId);
  if (!section) {
    return;
  }
  addListBlock(section);
  updateContent(nextContent);
}

function handleAccept(blockId: string) {
  if (!draftDocument.value) {
    return;
  }
  updateContent(acceptPendingBlock(draftDocument.value.content, blockId));
}

function handleReject(blockId: string) {
  if (!draftDocument.value) {
    return;
  }
  updateContent(rejectPendingBlock(draftDocument.value.content, blockId));
}

function getConfirmedEntries(section: SectionBlock) {
  return section.children
    .map((child, index) => ({ child, index }))
    .filter((entry) => entry.child.status === 'confirmed');
}

function getPendingEntries(section: SectionBlock) {
  return section.children
    .map((child, index) => ({ child, index }))
    .filter((entry) => entry.child.status === 'pending');
}

function scrollToSection(sectionId: string) {
  document.getElementById(`section-${sectionId}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function startGeneration(sectionId?: string) {
  if (!authStore.token) {
    return;
  }

  streamError.value = '';
  generationProgress.isGenerating = true;
  generationProgress.completed = 0;
  generationProgress.total = 0;
  generationProgress.currentSection = '';
  activeSectionId.value = sectionId ?? null;

  try {
    const response = await startGenerationMutation.mutateAsync(sectionId);
    await consumeGenerationStream(response.stream_url, authStore.token, {
      onEvent(event, payload) {
        if (event === 'status') {
          const state = (payload as { state: string }).state;
          generationProgress.isGenerating = state === 'generating';
          if (state === 'ready') {
            activeSectionId.value = null;
          }
        }
        if (event === 'progress') {
          const progress = payload as {
            completed: number;
            total: number;
            current_section: string;
            section_id: string;
          };
          generationProgress.completed = progress.completed;
          generationProgress.total = progress.total;
          generationProgress.currentSection = progress.current_section;
          activeSectionId.value = progress.section_id;
        }
        if (event === 'document') {
          applyServerDocument(payload as LessonDocument);
        }
        if (event === 'done') {
          generationProgress.isGenerating = false;
          activeSectionId.value = null;
          void taskQuery.refetch();
          void documentsQuery.refetch();
        }
        if (event === 'error') {
          streamError.value = (payload as { message: string }).message;
          generationProgress.isGenerating = false;
        }
      },
    });
  } catch {
    streamError.value = '生成流打开失败，请稍后重试。';
    generationProgress.isGenerating = false;
  }
}

async function refreshFromServer() {
  const response = await documentsQuery.refetch();
  const document = response.data?.items[0];
  if (document) {
    applyServerDocument(document);
  }
}

async function handleExport() {
  if (!draftDocument.value || !taskQuery.data.value) {
    return;
  }
  await exportDocx(draftDocument.value.id, taskQuery.data.value.title);
}
</script>

<template>
  <div class="page-shell">
    <header class="app-header app-card">
      <div>
        <button class="button ghost" type="button" @click="router.push({ name: 'tasks' })">
          返回备课台
        </button>
        <div class="brand" style="margin-top: 10px">
          {{ taskQuery.data.value?.title || '教案编辑器' }}
        </div>
        <div class="task-meta">
          {{ taskQuery.data.value?.subject }} · {{ taskQuery.data.value?.grade }} ·
          {{ taskQuery.data.value?.topic }}
        </div>
      </div>
      <div class="header-actions">
        <div class="save-indicator" :class="{ conflict: saveState === 'conflict' }">
          <template v-if="saveState === 'saved'">已保存</template>
          <template v-else-if="saveState === 'saving'">保存中...</template>
          <template v-else-if="saveState === 'dirty'">未保存的更改</template>
          <template v-else>保存冲突，请刷新后重试</template>
        </div>
        <button class="button secondary" type="button" @click="handleExport" :disabled="!draftDocument">
          导出 Word
        </button>
      </div>
    </header>

    <div v-if="taskQuery.isLoading.value || documentsQuery.isLoading.value" class="app-card empty-state">
      正在加载编辑器...
    </div>

    <div v-else-if="!draftDocument" class="app-card empty-state">
      没有找到教案文档。
    </div>

    <div v-else class="editor-layout">
      <aside class="outline-panel app-card">
        <h3>大纲导航</h3>
        <div class="outline-list">
          <button
            v-for="section in sections"
            :key="section.id"
            class="outline-item"
            :class="{ active: activeSectionId === section.id }"
            type="button"
            @click="scrollToSection(section.id)"
          >
            {{ section.title }}
          </button>
        </div>
      </aside>

      <main class="editor-panel app-card">
        <div class="editor-toolbar">
          <div>
            <h1 class="page-title" style="font-size: 28px; margin-bottom: 4px">
              结构化教案编辑器
            </h1>
            <div class="task-meta">结构可见、AI 内联、老师最后确认。</div>
          </div>
          <div class="button-row">
            <button class="button secondary" type="button" @click="startGeneration()">
              重新生成整份教案
            </button>
            <button
              v-if="saveState === 'conflict'"
              class="button ghost"
              type="button"
              @click="refreshFromServer"
            >
              刷新最新版本
            </button>
          </div>
        </div>

        <div v-if="generationProgress.isGenerating" class="generation-banner">
          正在生成 {{ generationProgress.currentSection || '教案内容' }}
          <template v-if="generationProgress.total">
            （{{ generationProgress.completed }}/{{ generationProgress.total }}）
          </template>
        </div>
        <div v-if="streamError" class="feedback">{{ streamError }}</div>

        <section
          v-for="section in sections"
          :id="`section-${section.id}`"
          :key="section.id"
          class="section-card"
        >
          <div class="editor-toolbar">
            <div>
              <h2 style="margin: 0">{{ section.title }}</h2>
              <div class="task-meta">
                {{ getConfirmedChildren(section).length }} 个已确认块，
                {{ getPendingChildren(section).length }} 个待确认块
              </div>
            </div>
            <div class="section-actions">
              <button class="button secondary" type="button" @click="appendParagraph(section.id)">
                添加段落
              </button>
              <button class="button secondary" type="button" @click="appendList(section.id)">
                添加列表
              </button>
              <button class="button ghost" type="button" @click="startGeneration(section.id)">
                AI 重新生成本节
              </button>
            </div>
          </div>

          <BlockRenderer
            v-for="entry in getConfirmedEntries(section)"
            :key="entry.child.id"
            :block="entry.child"
            @update:block="updateSectionChild(section.id, entry.index, $event)"
          />

          <PendingBlockCard
            v-for="entry in getPendingEntries(section)"
            :key="entry.child.id"
            :block="entry.child"
            @accept="handleAccept(entry.child.id)"
            @reject="handleReject(entry.child.id)"
          />

          <div
            v-if="getConfirmedEntries(section).length === 0 && getPendingEntries(section).length === 0"
            class="muted"
          >
            这一节还没有内容，你可以手动补充，或者使用 AI 生成。
          </div>
        </section>
      </main>
    </div>
  </div>
</template>
