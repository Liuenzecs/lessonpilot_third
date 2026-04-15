<script setup lang="ts">
import { computed } from 'vue';

import EditorShellHeader from '@/features/editor/components/EditorShellHeader.vue';
import EditorStatusBanner from '@/features/editor/components/EditorStatusBanner.vue';
import EditorToolbar from '@/features/editor/components/EditorToolbar.vue';
import ExportPreviewModal from '@/features/editor/components/ExportPreviewModal.vue';
import HistoryDrawer from '@/features/editor/components/HistoryDrawer.vue';
import SectionPanel from '@/features/editor/components/SectionPanel.vue';
import StreamingText from '@/features/editor/components/StreamingText.vue';
import { useEditorView } from '@/features/editor/composables/useEditorView';
import { getAppErrorState } from '@/shared/api/errors';
import StatePanel from '@/shared/components/StatePanel.vue';

import '@/features/editor/styles/editor.css';

const {
  router,
  taskQuery,
  documentsQuery,
  draftDocument,
  saveState,
  streamError,
  historyOpen,
  exportMenuOpen,
  exportPreviewOpen,
  outlineCollapsed,
  isMobileViewport,
  selectedSnapshotId,
  notice,
  generationProgress,
  rewriteState,
  sections,
  currentDocType,
  hasMultipleDocs,
  activeDocTabIndex,
  historyQuery,
  snapshotQuery,
  previewSnapshot,
  showInitialSkeleton,
  hasPending,
  allCollapsed,
  collapsedSections,
  persistDocument,
  scrollToSection,
  startGeneration,
  stopGeneration,
  startSectionRewrite,
  refreshFromServer,
  handleExport,
  handleExportAll,
  openExportPreview,
  restoreSnapshot,
  confirmSectionByName,
  confirmAll,
  getSectionData,
  updateSectionData,
  toggleSectionCollapse,
  toggleAllSections,
} = useEditorView();

const editorErrorState = computed(() => {
  if (draftDocument.value) return null;
  const error = taskQuery.error.value ?? documentsQuery.error.value;
  if (!error) return null;
  return getAppErrorState(error, {
    defaultTitle: '教案暂时打不开',
    defaultDescription: '你可以重试，或者先回到备课台继续其他工作。',
  });
});

const showMissingState = computed(
  () => !showInitialSkeleton.value && !draftDocument.value && !editorErrorState.value,
);

function getStreamingTextForSection(sectionName: string): string {
  if (generationProgress.isGenerating && generationProgress.currentSectionName === sectionName) {
    return generationProgress.streamingText;
  }
  if (rewriteState.isRewriting && rewriteState.sectionName === sectionName) {
    return rewriteState.streamingText;
  }
  return '';
}

function isRewritingSection(sectionName: string): boolean {
  return rewriteState.isRewriting && rewriteState.sectionName === sectionName;
}
</script>

<template>
  <div class="page-shell editor-shell-page">
    <EditorShellHeader
      :task="taskQuery.data.value ?? null"
      :save-state="saveState"
      :outline-collapsed="outlineCollapsed"
      :export-menu-open="exportMenuOpen"
      :has-multiple-docs="hasMultipleDocs"
      @back="router.push({ name: 'tasks' })"
      @toggle-outline="outlineCollapsed = !outlineCollapsed"
      @open-history="historyOpen = true"
      @toggle-export-menu="exportMenuOpen = !exportMenuOpen"
      @export="handleExport"
      @export-all="handleExportAll"
      @open-export-preview="openExportPreview"
      @refresh="refreshFromServer"
      @retry-save="persistDocument"
    />

    <StatePanel
      v-if="editorErrorState"
      icon="🧾"
      eyebrow="编辑器"
      :title="editorErrorState.title"
      :description="editorErrorState.description"
      tone="error"
    >
      <template #actions>
        <button class="button primary" type="button" @click="refreshFromServer">重试</button>
        <button class="button ghost" type="button" @click="router.push({ name: 'tasks' })">返回备课台</button>
      </template>
    </StatePanel>

    <StatePanel
      v-else-if="isMobileViewport"
      icon="📱"
      eyebrow="编辑器"
      title="请在平板或电脑上使用编辑器"
      description="为了保证编辑体验，手机端暂不支持编辑器。"
      tone="info"
    >
      <template #actions>
        <button class="button primary" type="button" @click="router.push({ name: 'tasks' })">回到备课台</button>
      </template>
    </StatePanel>

    <div v-else-if="showInitialSkeleton || draftDocument" class="editor-layout" :class="{ 'outline-collapsed': outlineCollapsed }">
      <aside v-if="!outlineCollapsed" class="outline-panel app-card">
        <div class="outline-panel-head">
          <h3 style="margin: 0">大纲导航</h3>
        </div>

        <div class="outline-list">
          <button
            v-for="section in sections"
            :key="section.name"
            class="outline-item"
            :class="{ active: section.name === generationProgress.currentSectionName }"
            type="button"
            @click="scrollToSection(section.name)"
          >
            <span class="outline-dot" />
            <span>{{ section.title }}</span>
            <span v-if="section.status === 'pending'" class="outline-badge">待确认</span>
          </button>
        </div>
      </aside>

      <main class="editor-panel app-card">
        <EditorStatusBanner
          :is-generating="generationProgress.isGenerating"
          :completed="generationProgress.completed"
          :total="generationProgress.total"
          :current-section="generationProgress.currentSection"
          :is-rewriting="rewriteState.isRewriting"
          :rewrite-action="rewriteState.action"
          :is-appending="false"
          :append-section-title="''"
          :stream-error="streamError"
          :notice-text="notice.text"
          :notice-tone="notice.tone"
          @stop="stopGeneration"
        />

        <!-- Tab switcher for tasks with both lesson_plan and study_guide -->
        <div v-if="hasMultipleDocs" class="doc-tabs">
          <button
            class="doc-tab"
            :class="{ active: activeDocTabIndex === 0 }"
            type="button"
            @click="activeDocTabIndex = 0"
          >
            教案
          </button>
          <button
            class="doc-tab"
            :class="{ active: activeDocTabIndex === 1 }"
            type="button"
            @click="activeDocTabIndex = 1"
          >
            学案
          </button>
        </div>

        <EditorToolbar
          :all-collapsed="allCollapsed"
          :has-pending="hasPending"
          @toggle-all="toggleAllSections"
          @confirm-all="confirmAll"
        />

        <div v-if="showInitialSkeleton" class="generation-banner">
          正在为你生成{{ currentDocType === 'study_guide' ? '学案' : '教案' }}...
        </div>

        <StreamingText
          v-if="generationProgress.isGenerating && generationProgress.streamingText && !generationProgress.currentSectionName"
          :text="generationProgress.streamingText"
          :active="generationProgress.isGenerating"
          class="streaming-inline"
        />

        <div class="section-stack">
          <div
            v-for="section in sections"
            :id="`section-${section.name}`"
            :key="section.name"
          >
            <SectionPanel
              :section="section"
              :doc-type="currentDocType"
              :section-data="getSectionData(section.name)"
              :collapsed="Boolean(collapsedSections[section.name])"
              :streaming-text="getStreamingTextForSection(section.name)"
              :is-rewriting="isRewritingSection(section.name)"
              @toggle-collapse="toggleSectionCollapse(section.name)"
              @update-section="updateSectionData(section.name, $event)"
              @confirm="confirmSectionByName(section.name)"
              @ai-action="startSectionRewrite(section.name, $event.action, $event.instruction)"
            />
          </div>
        </div>
      </main>
    </div>

    <StatePanel
      v-else-if="showMissingState"
      icon="🗂"
      eyebrow="编辑器"
      title="没有找到这份教案文档"
      description="它可能已被删除，或者当前任务还没有创建成功。"
      tone="empty"
    >
      <template #actions>
        <button class="button primary" type="button" @click="router.push({ name: 'tasks' })">返回备课台</button>
      </template>
    </StatePanel>

    <HistoryDrawer
      :open="historyOpen"
      :loading="historyQuery.isLoading.value"
      :preview-loading="snapshotQuery.isLoading.value"
      :items="historyQuery.data.value?.items ?? []"
      :preview-snapshot="previewSnapshot"
      :selected-snapshot-id="selectedSnapshotId || null"
      @close="historyOpen = false"
      @select="selectedSnapshotId = $event"
      @restore="restoreSnapshot"
    />

    <ExportPreviewModal
      :open="exportPreviewOpen"
      :task="taskQuery.data.value ?? null"
      :content="draftDocument?.content ?? null"
      @close="exportPreviewOpen = false"
    />
  </div>
</template>
