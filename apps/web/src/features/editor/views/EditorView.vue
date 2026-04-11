<script setup lang="ts">
import EditorQuickActionsBar from '@/features/editor/components/EditorQuickActionsBar.vue';
import EditorSectionCard from '@/features/editor/components/EditorSectionCard.vue';
import EditorShellHeader from '@/features/editor/components/EditorShellHeader.vue';
import EditorStatusBanner from '@/features/editor/components/EditorStatusBanner.vue';
import ExportPreviewModal from '@/features/editor/components/ExportPreviewModal.vue';
import HistoryDrawer from '@/features/editor/components/HistoryDrawer.vue';
import { useEditorView } from '@/features/editor/composables/useEditorView';

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
  setSectionElement,
  handleBlockUpdate,
  handleMove,
  handleDelete,
  handleConvert,
  handleReorder,
  handleAccept,
  handleReject,
  handleAppendToContainer,
  scrollToSection,
  isSectionShowingSkeleton,
  startGeneration,
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
} = useEditorView();
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
      @open-history="historyOpen = true"
      @toggle-export-menu="exportMenuOpen = !exportMenuOpen"
      @export="handleExport"
      @open-export-preview="openExportPreview"
      @refresh="refreshFromServer"
    />

    <div v-if="taskQuery.isLoading.value || documentsQuery.isLoading.value" class="app-card empty-state">
      正在加载编辑器...
    </div>

    <div v-else-if="!draftDocument" class="app-card empty-state">没有找到教案文档。</div>

    <div v-else class="editor-layout" :class="{ 'outline-collapsed': outlineCollapsed }">
      <aside v-if="!outlineCollapsed" class="outline-panel app-card">
        <div class="outline-panel-head">
          <div>
            <h3 style="margin: 0">大纲导航</h3>
            <div class="muted">让结构先于内容出现</div>
          </div>
        </div>

        <div class="outline-list">
          <button
            v-for="section in sections"
            :key="section.id"
            class="outline-item"
            :class="{ active: highlightedSectionId === section.id }"
            type="button"
            @click="scrollToSection(section.id)"
          >
            <span class="outline-dot" />
            <span>{{ section.title }}</span>
          </button>
        </div>
      </aside>

      <main class="editor-panel app-card">
        <div class="editor-panel-head">
          <div>
            <div class="editor-eyebrow">结构化教案编辑器</div>
            <p class="subtitle editor-panel-subtitle">结构可见、AI 内联、操作极简，老师最后确认。</p>
          </div>
          <div class="button-row">
            <button class="button ghost" type="button" @click="startGeneration()">重新生成整份教案</button>
          </div>
        </div>

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
        />

        <div class="section-stack">
          <div
            v-for="section in sections"
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
              @accept-pending="handleAccept"
              @reject-pending="handleReject"
              @regenerate-pending="
                startRewrite({
                  mode: 'block',
                  targetBlockId: $event.targetBlockId,
                  action: $event.action,
                })
              "
              @regenerate-section="startGeneration($event)"
            />
          </div>
        </div>

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
      </main>
    </div>

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
