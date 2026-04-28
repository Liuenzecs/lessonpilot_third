<script setup lang="ts">
import { computed } from 'vue';
import { List, ClipboardCheck, StickyNote, ArrowLeft } from 'lucide-vue-next';

import EditorShellHeader from '@/features/editor/components/EditorShellHeader.vue';
import EditorStatusBanner from '@/features/editor/components/EditorStatusBanner.vue';
import EditorToolbar from '@/features/editor/components/EditorToolbar.vue';
import ExportQualityPanel from '@/features/editor/components/ExportQualityPanel.vue';
import ExportPreviewModal from '@/features/editor/components/ExportPreviewModal.vue';
import HistoryDrawer from '@/features/editor/components/HistoryDrawer.vue';
import SectionPanel from '@/features/editor/components/SectionPanel.vue';
import StreamingText from '@/features/editor/components/StreamingText.vue';
import TeachingPackagePanel from '@/features/editor/components/TeachingPackagePanel.vue';
import { useEditorView } from '@/features/editor/composables/useEditorView';
import SharePanel from '@/features/sharing/components/SharePanel.vue';
import ReimportPanel from '@/features/reimport/components/ReimportPanel.vue';
import { getAppErrorState } from '@/shared/api/errors';
import StatePanel from '@/shared/components/StatePanel.vue';

import '@/features/editor/styles/editor.css';
import '@/features/editor/styles/editor-fields.css';

const {
  router,
  taskQuery,
  documentsQuery,
  draftDocument,
  saveState,
  streamError,
  historyOpen,
  exportMenuOpen,
  sharePanelOpen,
  reimportPanelOpen,
  exportPreviewOpen,
  qualityPanelOpen,
  qualityResult,
  qualityChecking,
  qualityFixing,
  selectedExportTemplateId,
  schoolTemplatesQuery,
  assetRecommendationsQuery,
  usePersonalAssetsForGeneration,
  selectedPersonalAssetIds,
  teachingPackageResult,
  teachingPackageGenerating,
  outlineCollapsed,
  isMobileViewport,
  mobileOutlineOpen,
  mobileInspectorOpen,
  selectedSnapshotId,
  notice,
  generationProgress,
  rewriteState,
  sections,
  currentDocType,
  currentDocumentId,
  currentDocumentVersion,
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
  stopGeneration,
  startSectionRewrite,
  refreshFromServer,
  handleExport,
  handleExportAll,
  runQualityCheck,
  applyQualityFix,
  exportAfterQualityCheck,
  generateTeachingPackage,
  startGenerationWithPersonalAssets,
  openExportPreview,
  restoreSnapshot,
  confirmSectionByName,
  confirmAll,
  getSectionData,
  getSectionReferences,
  updateSectionData,
  togglePersonalAssetSelection,
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

const pendingSectionCount = computed(() =>
  sections.value.filter((section) => section.status === 'pending').length,
);

const referenceCount = computed(() =>
  sections.value.reduce((total, section) => total + getSectionReferences(section.name).length, 0),
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
      :current-doc-type="currentDocType"
      :quality-readiness="qualityResult?.readiness ?? null"
      :quality-checking="qualityChecking"
      @back="router.push({ name: 'tasks' })"
      @toggle-outline="outlineCollapsed = !outlineCollapsed"
      @open-history="historyOpen = true"
      @open-share="sharePanelOpen = true"
      @open-reimport="reimportPanelOpen = true"
      @toggle-export-menu="exportMenuOpen = !exportMenuOpen"
      @export="handleExport"
      @export-all="handleExportAll"
      @open-export-preview="openExportPreview"
      @quality-check="runQualityCheck"
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

    <div v-else-if="showInitialSkeleton || draftDocument" class="editor-layout" :class="{ 'outline-collapsed': outlineCollapsed, 'editor-layout--mobile': isMobileViewport }">
      <aside v-if="!outlineCollapsed" class="outline-panel">
        <div class="outline-panel-head">
          <h3>文档目录</h3>
          <p class="outline-panel-copy">{{ pendingSectionCount }} 节待确认</p>
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

      <main class="editor-panel">
        <div class="editor-panel-head">
          <EditorStatusBanner
            :is-generating="generationProgress.isGenerating"
            :completed="generationProgress.completed"
            :total="generationProgress.total"
            :current-section="generationProgress.currentSection"
            :rag-status="generationProgress.ragStatus"
            :asset-status="generationProgress.assetStatus"
            :is-rewriting="rewriteState.isRewriting"
            :rewrite-action="rewriteState.action"
            :is-appending="false"
            :append-section-title="''"
            :stream-error="streamError"
            :notice-text="notice.text"
            :notice-tone="notice.tone"
            @stop="stopGeneration"
          />

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

          <div class="editor-toolbar-row">
            <EditorToolbar
              :all-collapsed="allCollapsed"
              :has-pending="hasPending"
              @toggle-all="toggleAllSections"
              @confirm-all="confirmAll"
            />
            <p class="editor-toolbar-note">文档会逐节自动保存；待确认内容不会直接混入最终导出。</p>
          </div>
        </div>

        <div v-if="showInitialSkeleton" class="generation-banner">
          正在整理{{ currentDocType === 'study_guide' ? '学案' : '教案' }}初稿...
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
              :section-references="getSectionReferences(section.name)"
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

      <aside class="editor-inspector-panel">
        <section class="inspector-section">
          <div class="inspector-section-head">
            <h3>导出前体检</h3>
            <span
              class="inspector-status"
              :class="qualityResult?.readiness ?? 'idle'"
            >
              {{ qualityResult?.readiness === 'ready' ? '可提交' : qualityResult?.readiness === 'blocked' ? '有阻断' : qualityResult?.readiness === 'needs_fixes' ? '需修复' : '未检查' }}
            </span>
          </div>
          <p class="inspector-copy">
            {{ qualityResult?.summary || '检查目标、过程、评价和导出风险。' }}
          </p>
          <button class="button secondary inspector-action" type="button" :disabled="qualityChecking" @click="() => runQualityCheck()">
            {{ qualityChecking ? '体检中...' : '运行体检' }}
          </button>
          <button v-if="qualityResult" class="button ghost inspector-action" type="button" @click="qualityPanelOpen = true">
            查看问题与修复建议
          </button>
        </section>

        <section class="inspector-section">
          <div class="inspector-section-head">
            <h3>学校格式</h3>
            <button class="button ghost" type="button" @click="router.push({ name: 'school-templates' })">管理</button>
          </div>
          <label class="editor-export-template-bar">
            <span>导出模板</span>
            <select v-model="selectedExportTemplateId">
              <option value="">默认 Word 格式</option>
              <option
                v-for="template in schoolTemplatesQuery.data.value ?? []"
                :key="template.id"
                :value="template.id"
              >
                {{ template.name }}
              </option>
            </select>
          </label>
        </section>

        <section class="inspector-section">
          <div class="inspector-section-head">
            <h3>参考资料</h3>
            <span class="inspector-status idle">{{ referenceCount }} 条引用</span>
          </div>
          <label class="personal-assets-toggle">
            <input v-model="usePersonalAssetsForGeneration" type="checkbox" />
            <span>参考我的资料库</span>
          </label>
          <div v-if="usePersonalAssetsForGeneration" class="personal-assets-picker">
            <button
              v-for="asset in assetRecommendationsQuery.data.value ?? []"
              :key="asset.asset_id"
              type="button"
              class="asset-choice-chip"
              :class="{ active: selectedPersonalAssetIds.includes(asset.asset_id) }"
              @click="togglePersonalAssetSelection(asset.asset_id)"
            >
              {{ asset.title }} · {{ asset.section_title }}
            </button>
            <p v-if="!(assetRecommendationsQuery.data.value ?? []).length" class="editor-toolbar-note">
              当前课题暂未匹配到个人资料。
            </p>
            <button class="button ghost inspector-action" type="button" @click="router.push({ name: 'personal-assets' })">
              管理资料
            </button>
            <button
              class="button secondary inspector-action"
              type="button"
              :disabled="generationProgress.isGenerating"
              @click="startGenerationWithPersonalAssets"
            >
              按当前资料重新整理
            </button>
          </div>
        </section>

        <TeachingPackagePanel
          :visible="currentDocType === 'lesson_plan'"
          :loading="teachingPackageGenerating"
          :package-result="teachingPackageResult"
          @generate="generateTeachingPackage"
        />
      </aside>
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

    <SharePanel
      :document-id="currentDocumentId"
      :open="sharePanelOpen"
      @close="sharePanelOpen = false"
    />

    <ReimportPanel
      :document-id="currentDocumentId"
      :document-version="currentDocumentVersion"
      :open="reimportPanelOpen"
      @close="reimportPanelOpen = false"
      @merged="refreshFromServer"
    />

    <ExportPreviewModal
      :open="exportPreviewOpen"
      :task="taskQuery.data.value ?? null"
      :content="draftDocument?.content ?? null"
      @close="exportPreviewOpen = false"
    />

    <ExportQualityPanel
      :open="qualityPanelOpen"
      :result="qualityResult"
      :loading="qualityChecking"
      :fixing="qualityFixing"
      @close="qualityPanelOpen = false"
      @export="exportAfterQualityCheck"
      @fix="applyQualityFix"
    />

    <!-- Mobile: bottom action bar -->
    <div v-if="isMobileViewport && draftDocument" class="editor-mobile-bottom-bar">
      <button
        class="mobile-bar-btn"
        :class="{ active: mobileOutlineOpen }"
        type="button"
        @click="mobileOutlineOpen = !mobileOutlineOpen; mobileInspectorOpen = false"
      >
        <List :size="20" />
        <span>目录</span>
      </button>
      <button
        class="mobile-bar-btn"
        type="button"
        @click="confirmAll"
      >
        <ClipboardCheck :size="20" />
        <span>全部确认</span>
      </button>
      <button
        class="mobile-bar-btn"
        :class="{ active: mobileInspectorOpen }"
        type="button"
        @click="mobileInspectorOpen = !mobileInspectorOpen; mobileOutlineOpen = false"
      >
        <StickyNote :size="20" />
        <span>检查</span>
      </button>
      <button
        class="mobile-bar-btn"
        type="button"
        @click="router.push({ name: 'tasks' })"
      >
        <ArrowLeft :size="20" />
        <span>返回</span>
      </button>
    </div>

    <!-- Mobile: outline bottom sheet -->
    <div v-if="isMobileViewport" class="outline-panel" :class="{ open: mobileOutlineOpen }">
      <div class="outline-panel-head">
        <h3>文档目录</h3>
        <p class="outline-panel-copy">{{ pendingSectionCount }} 节待确认</p>
      </div>
      <div class="outline-list">
        <button
          v-for="section in sections"
          :key="section.name"
          class="outline-item"
          :class="{ active: section.name === generationProgress.currentSectionName }"
          type="button"
          @click="scrollToSection(section.name); mobileOutlineOpen = false"
        >
          <span class="outline-dot" />
          <span>{{ section.title }}</span>
          <span v-if="section.status === 'pending'" class="outline-badge">待确认</span>
        </button>
      </div>
    </div>

    <!-- Mobile: inspector bottom sheet -->
    <div v-if="isMobileViewport && draftDocument" class="editor-inspector-panel" :class="{ open: mobileInspectorOpen }">
      <section class="inspector-section">
        <div class="inspector-section-head">
          <h3>导出前体检</h3>
          <span class="inspector-status" :class="qualityResult?.readiness ?? 'idle'">
            {{ qualityResult?.readiness === 'ready' ? '可提交' : qualityResult?.readiness === 'blocked' ? '有阻断' : qualityResult?.readiness === 'needs_fixes' ? '需修复' : '未检查' }}
          </span>
        </div>
        <button class="button secondary inspector-action" type="button" :disabled="qualityChecking" @click="() => runQualityCheck()">
          {{ qualityChecking ? '体检中...' : '运行体检' }}
        </button>
        <button
          v-if="qualityResult"
          class="button ghost inspector-action"
          type="button"
          @click="qualityPanelOpen = true; mobileInspectorOpen = false"
        >
          查看问题与修复建议
        </button>
      </section>
      <section class="inspector-section">
        <div class="inspector-section-head">
          <h3>导出</h3>
        </div>
        <button class="button secondary inspector-action" type="button" @click="handleExport('docx'); mobileInspectorOpen = false">
          导出 Word
        </button>
        <button class="button ghost inspector-action" type="button" @click="handleExport('pptx'); mobileInspectorOpen = false">
          导出 PPTX
        </button>
      </section>
    </div>

    <!-- Mobile: overlay backdrop -->
    <div
      v-if="isMobileViewport && (mobileOutlineOpen || mobileInspectorOpen)"
      class="editor-mobile-overlay"
      @click="mobileOutlineOpen = false; mobileInspectorOpen = false"
    />
  </div>
</template>
