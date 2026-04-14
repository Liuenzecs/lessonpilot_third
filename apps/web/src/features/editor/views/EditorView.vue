<script setup lang="ts">
import { computed } from 'vue';

import EditorQuickActionsBar from '@/features/editor/components/EditorQuickActionsBar.vue';
import EditorSectionCard from '@/features/editor/components/EditorSectionCard.vue';
import EditorSectionSkeleton from '@/features/editor/components/EditorSectionSkeleton.vue';
import EditorShellHeader from '@/features/editor/components/EditorShellHeader.vue';
import EditorStatusBanner from '@/features/editor/components/EditorStatusBanner.vue';
import ExportPreviewModal from '@/features/editor/components/ExportPreviewModal.vue';
import HistoryDrawer from '@/features/editor/components/HistoryDrawer.vue';
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
  activeBlockId,
  openMenuBlockId,
  historyOpen,
  exportMenuOpen,
  exportPreviewOpen,
  outlineCollapsed,
  isMobileViewport,
  selectedSnapshotId,
  appendComposerOpen,
  appendInstruction,
  notice,
  generationProgress,
  rewriteState,
  appendState,
  sections,
  historyQuery,
  snapshotQuery,
  previewSnapshot,
  currentSectionId,
  currentSectionTitle,
  highlightedSectionId,
  confirmedPreviewBlocks,
  showInitialSkeleton,
  skeletonSectionTitles,
  setSectionElement,
  persistDocument,
  handleBlockUpdate,
  handleMove,
  handleDelete,
  handleConvert,
  handleReorder,
  handleAccept,
  handleReject,
  handleIndentBlock,
  handleInsertParagraphAfter,
  handleInsertListItem,
  handleExitListToParagraph,
  handleAppendToContainer,
  scrollToSection,
  isSectionShowingSkeleton,
  startGeneration,
  stopGeneration,
  startRewrite,
  startAppend,
  refreshFromServer,
  handleExport,
  openExportPreview,
  restoreSnapshot,
  handleBottomAddParagraph,
  handleBottomAddExercise,
  toggleAppendComposer,
  cancelAppendComposer,
  openHistoryDrawer,
} = useEditorView();

const editorErrorState = computed(() => {
  if (draftDocument.value) {
    return null;
  }

  const error = taskQuery.error.value ?? documentsQuery.error.value;
  if (!error) {
    return null;
  }

  return getAppErrorState(error, {
    defaultTitle: '教案暂时打不开',
    defaultDescription: '你可以重试，或者先回到备课台继续其他工作。',
  });
});

const showMissingState = computed(
  () => !showInitialSkeleton.value && !draftDocument.value && !editorErrorState.value,
);

function findSectionIdByTitle(sectionTitle: string) {
  return sections.value.find((section) => section.title === sectionTitle)?.id ?? null;
}
</script>

<template>
  <div class="page-shell editor-shell-page">
    <EditorShellHeader
      :task="taskQuery.data.value ?? null"
      :save-state="saveState"
      :outline-collapsed="outlineCollapsed"
      :export-menu-open="exportMenuOpen"
      @back="router.push({ name: 'tasks' })"
      @toggle-outline="outlineCollapsed = !outlineCollapsed"
      @open-history="openHistoryDrawer"
      @toggle-export-menu="exportMenuOpen = !exportMenuOpen"
      @export="handleExport"
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
        <button class="button ghost" type="button" @click="router.push({ name: 'help' })">去帮助中心</button>
      </template>
    </StatePanel>

    <StatePanel
      v-else-if="isMobileViewport"
      icon="📱"
      eyebrow="编辑器"
      title="请在平板或电脑上使用编辑器"
      description="为了保证结构导航、内联 AI 待确认和导出预览的体验，手机端不再强行压缩编辑器。"
      tone="info"
    >
      <template #actions>
        <button class="button primary" type="button" @click="router.push({ name: 'tasks' })">回到备课台</button>
        <button class="button ghost" type="button" @click="router.push({ name: 'help' })">查看帮助</button>
      </template>
    </StatePanel>

    <div v-else-if="showInitialSkeleton || draftDocument" class="editor-layout" :class="{ 'outline-collapsed': outlineCollapsed }">
      <aside
        v-if="!outlineCollapsed"
        class="outline-panel app-card"
      >
        <div class="outline-panel-head">
          <h3 style="margin: 0">大纲导航</h3>
        </div>

        <div class="outline-list">
          <button
            v-for="sectionTitle in showInitialSkeleton ? skeletonSectionTitles : sections.map((section) => section.title)"
            :key="sectionTitle"
            class="outline-item"
            :class="{
              active: !showInitialSkeleton && findSectionIdByTitle(sectionTitle) === highlightedSectionId,
            }"
            type="button"
            @click="!showInitialSkeleton && findSectionIdByTitle(sectionTitle) && scrollToSection(findSectionIdByTitle(sectionTitle)!)"
          >
            <span class="outline-dot" />
            <span>{{ sectionTitle }}</span>
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
          :is-appending="appendState.isAppending"
          :append-section-title="appendState.sectionTitle"
          :stream-error="streamError"
          :notice-text="notice.text"
          :notice-tone="notice.tone"
          @stop="stopGeneration"
        />

        <div v-if="showInitialSkeleton" class="generation-banner">
          正在为你生成教案...
        </div>

        <div class="section-stack">
          <template v-if="showInitialSkeleton">
            <EditorSectionSkeleton
              v-for="sectionTitle in skeletonSectionTitles"
              :key="sectionTitle"
              :title="sectionTitle"
              :is-current="generationProgress.currentSection === sectionTitle || !generationProgress.currentSection"
            />
          </template>

          <StreamingText
            v-if="generationProgress.isGenerating && generationProgress.streamingText"
            :text="generationProgress.streamingText"
            :active="generationProgress.isGenerating"
            class="streaming-inline"
          />

          <div
            v-for="section in sections"
            v-else
            :id="`section-${section.id}`"
            :key="section.id"
            :data-section-id="section.id"
            :ref="(element) => setSectionElement(section.id, element as Element | null)"
          >
            <EditorSectionCard
              :section="section"
              :active-block-id="activeBlockId"
              :open-menu-block-id="openMenuBlockId"
              :loading-target-id="rewriteState.targetBlockId"
              :show-skeleton="isSectionShowingSkeleton(section.id, section.children.length)"
              :is-current-generating="generationProgress.currentSectionId === section.id"
              @activate="activeBlockId = $event"
              @update:block="handleBlockUpdate"
              @toggle-menu="openMenuBlockId = $event"
              @move="handleMove($event.blockId, $event.direction)"
              @delete="handleDelete"
              @convert="handleConvert($event.blockId, $event.targetType)"
              @rewrite="startRewrite({ mode: 'block', targetBlockId: $event.blockId, action: $event.action })"
              @reorder="handleReorder($event.draggedId, $event.targetId, $event.parentId)"
              @add-child="handleAppendToContainer($event.parentId, $event.type)"
              @selection-rewrite="
                startRewrite({
                  mode: 'selection',
                  targetBlockId: $event.blockId,
                  action: $event.action,
                  selectionText: $event.selectionText,
                })
              "
              @insert-paragraph-after="handleInsertParagraphAfter"
              @indent-block="handleIndentBlock($event.blockId, $event.direction)"
              @list-insert-item="handleInsertListItem($event.blockId, $event.index)"
              @list-exit-to-paragraph="handleExitListToParagraph($event.blockId, $event.index)"
              @accept-pending="handleAccept"
              @reject-pending="handleReject"
              @regenerate-pending="
                startRewrite({
                  mode: $event.mode,
                  targetBlockId: $event.targetBlockId,
                  action: $event.action,
                  selectionText: $event.selectionText,
                })
              "
              @regenerate-section="startGeneration($event)"
            />
          </div>
        </div>

        <div v-if="draftDocument">
          <EditorQuickActionsBar
            :current-section-title="currentSectionTitle"
            :append-open="appendComposerOpen"
            :append-instruction="appendInstruction"
            :append-loading="appendState.isAppending"
            :disabled="!currentSectionId"
            @add-paragraph="handleBottomAddParagraph"
            @add-exercise="handleBottomAddExercise"
            @toggle-append="toggleAppendComposer"
            @update:append-instruction="appendInstruction = $event"
            @submit-append="startAppend"
            @cancel-append="cancelAppendComposer"
          />
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
      :blocks="confirmedPreviewBlocks"
      @close="exportPreviewOpen = false"
    />
  </div>
</template>
