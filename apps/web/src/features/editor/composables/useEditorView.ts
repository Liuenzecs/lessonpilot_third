/**
 * 编辑器主 composable。
 * 组合 useAutoSave、useEditorGeneration、useEditorRewrite，
 * 管理文档加载、Tab 切换、section 状态。
 */
import type { SectionInfo } from '@lessonpilot/shared-types';
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import {
  useDocumentHistory,
  useDocumentSnapshot,
  useQualityCheckMutation,
  useQualityFixMutation,
  useRestoreSnapshotMutation,
  useTaskDocuments,
  useTeachingPackageMutation,
} from '@/features/editor/composables/useEditor';
import { useAutoSave } from '@/features/editor/composables/useAutoSave';
import { useEditorGeneration } from '@/features/editor/composables/useEditorGeneration';
import { useEditorRewrite } from '@/features/editor/composables/useEditorRewrite';
import type {
  DocumentSnapshotRecord,
  LessonDocument,
  QualityCheckResponse,
  QualityIssue,
  TeachingPackageRecord,
} from '@/features/editor/types';
import { exportDocx, exportMultipleDocx, exportPptx } from '@/features/export/composables/useExport';
import { usePersonalAssetRecommendations, useSchoolTemplates, useTask } from '@/features/task/composables/useTasks';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';
import {
  cloneSerializable,
  confirmAllSections,
  confirmSection as confirmSectionUtil,
  getSectionContent,
  getSectionReferences as getSectionReferencesUtil,
  getSections,
  updateSection,
} from '@/shared/utils/content';

export function useEditorView() {
  const router = useRouter();
  const route = useRoute();
  const toast = useToast();

  const taskId = computed(() => String(route.params.taskId ?? ''));
  const taskQuery = useTask(taskId.value);
  const documentsQuery = useTaskDocuments(taskId.value);
  const draftDocument = ref<LessonDocument | null>(null);
  const saveState = ref<'saved' | 'dirty' | 'saving' | 'retrying' | 'error' | 'conflict'>('saved');
  const streamError = ref('');
  const suppressAutosave = ref(false);
  const initialGenerationTriggered = ref(false);
  const historyOpen = ref(false);
  const exportMenuOpen = ref(false);
  const exportPreviewOpen = ref(false);
  const qualityPanelOpen = ref(false);
  const qualityResult = ref<QualityCheckResponse | null>(null);
  const selectedExportTemplateId = ref('');
  const teachingPackageResult = ref<TeachingPackageRecord | null>(null);
  const usePersonalAssetsForGeneration = ref(false);
  const selectedPersonalAssetIds = ref<string[]>([]);
  const outlineCollapsed = ref(typeof window !== 'undefined' ? window.innerWidth < 1100 : false);
  const isMobileViewport = ref(typeof window !== 'undefined' ? window.innerWidth < 720 : false);
  const selectedSnapshotId = ref('');
  const collapsedSections = ref<Record<string, boolean>>({});
  const activeDocTabIndex = ref(0);

  const primaryDocument = computed(() => documentsQuery.data.value?.items[0] ?? null);
  // Current active document based on tab
  const activeDocument = computed(() => {
    const docs = documentsQuery.data.value?.items ?? [];
    if (docs.length <= 1) return draftDocument.value ?? docs[0] ?? null;
    return draftDocument.value ?? docs[activeDocTabIndex.value] ?? docs[0];
  });

  const currentDocType = computed(() => activeDocument.value?.doc_type ?? 'lesson_plan');
  const sections = computed<SectionInfo[]>(() =>
    draftDocument.value ? getSections(draftDocument.value.content) : [],
  );

  // History
  const currentDocumentId = computed(() => activeDocument.value?.id ?? '');
  const historyEnabled = computed(() => historyOpen.value && Boolean(currentDocumentId.value));
  const snapshotEnabled = computed(() => historyEnabled.value && Boolean(selectedSnapshotId.value));
  const historyQuery = useDocumentHistory(currentDocumentId, historyEnabled);
  const snapshotQuery = useDocumentSnapshot(currentDocumentId, selectedSnapshotId, snapshotEnabled);
  const restoreSnapshotMutation = useRestoreSnapshotMutation(
    () => currentDocumentId.value,
    () => taskId.value,
  );
  const qualityCheckMutation = useQualityCheckMutation(() => currentDocumentId.value);
  const qualityFixMutation = useQualityFixMutation(
    () => currentDocumentId.value,
    () => taskId.value,
  );
  const teachingPackageMutation = useTeachingPackageMutation(() => currentDocumentId.value);
  const schoolTemplatesQuery = useSchoolTemplates();
  const assetRecommendationsQuery = usePersonalAssetRecommendations(() => ({
    subject: taskQuery.data.value?.subject ?? '',
    grade: taskQuery.data.value?.grade ?? '',
    topic: taskQuery.data.value?.topic ?? '',
    keywords: taskQuery.data.value?.requirements ?? '',
  }));
  const previewSnapshot = computed<DocumentSnapshotRecord | null>(() => snapshotQuery.data.value ?? null);

  const notice = reactive<{ text: string; tone: 'success' | 'info' }>({ text: '', tone: 'success' });

  // Auto-save
  function applyServerDocument(doc: LessonDocument) {
    suppressAutosave.value = true;
    draftDocument.value = cloneSerializable(doc);
    saveState.value = 'saved';
    nextTick(() => { suppressAutosave.value = false; });
  }

  const { persistDocument, ensureLatestDocumentSaved, handleOnline, handleOffline } = useAutoSave({
    draftDocument,
    saveState,
    streamError,
    suppressAutosave,
    taskId: taskId.value,
    onApplyServerDocument: applyServerDocument,
  });

  // Generation
  const { generationProgress, startGeneration, stopGeneration } = useEditorGeneration({
    taskId: taskId.value,
    ensureLatestDocumentSaved,
    onApplyServerDocument: applyServerDocument,
    onRefetch: () => {
      void taskQuery.refetch();
      void documentsQuery.refetch();
      if (historyOpen.value) void historyQuery.refetch();
    },
    getSectionsCount: () => sections.value.length,
  });

  // Rewrite
  const { rewriteState, startSectionRewrite } = useEditorRewrite({
    draftDocument,
    streamError,
    ensureLatestDocumentSaved,
    onApplyServerDocument: applyServerDocument,
    onRefetch: () => {
      void documentsQuery.refetch();
      if (historyOpen.value) void historyQuery.refetch();
    },
  });

  // Initial document loading
  watch(
    primaryDocument,
    (doc) => {
      if (!doc) return;
      if (!draftDocument.value || saveState.value === 'saved') {
        applyServerDocument(doc);
      }
    },
    { immediate: true },
  );

  // Tab switching: load the selected document into draftDocument
  watch(activeDocTabIndex, (newIndex) => {
    const docs = documentsQuery.data.value?.items ?? [];
    if (docs.length <= 1) return;
    const doc = docs[newIndex];
    if (doc) {
      applyServerDocument(doc);
      collapsedSections.value = {};
    }
  });

  // Auto-trigger generation for new tasks
  watch(
    [taskQuery.data, primaryDocument],
    ([task, doc]) => {
      if (!task || !doc || initialGenerationTriggered.value) return;
      const secs = getSections(doc.content);
      const hasContent = secs.some((s) => s.status !== 'pending' || _sectionHasActualContent(getSectionData(s.name)));
      if (task.status === 'draft' && !hasContent) {
        initialGenerationTriggered.value = true;
        const routeOptions = _generationOptionsFromRoute();
        usePersonalAssetsForGeneration.value = routeOptions.usePersonalAssets;
        selectedPersonalAssetIds.value = routeOptions.personalAssetIds;
        void startGeneration({
          usePersonalAssets: routeOptions.usePersonalAssets,
          personalAssetIds: routeOptions.personalAssetIds,
        });
      }
    },
    { immediate: true },
  );

  // History auto-select
  watch(
    () => historyQuery.data.value?.items,
    (items) => {
      if (!historyOpen.value || !items?.length) return;
      if (!selectedSnapshotId.value || !items.some((item) => item.id === selectedSnapshotId.value)) {
        selectedSnapshotId.value = items[0].id;
      }
    },
    { immediate: true },
  );

  watch(historyOpen, (open) => {
    if (!open) selectedSnapshotId.value = '';
  });

  // Helpers
  function _sectionHasActualContent(data: unknown): boolean {
    if (Array.isArray(data)) return data.length > 0;
    if (typeof data === 'string') return data.trim().length > 0;
    if (data && typeof data === 'object') {
      return Object.values(data as Record<string, unknown>).some((v) => _sectionHasActualContent(v));
    }
    return false;
  }

  function getSectionData(sectionName: string): unknown {
    if (!draftDocument.value) return null;
    return getSectionContent(draftDocument.value.content, sectionName) ?? null;
  }

  function getSectionReferences(sectionName: string) {
    if (!draftDocument.value) return [];
    return getSectionReferencesUtil(draftDocument.value.content, sectionName);
  }

  function updateSectionData(sectionName: string, value: unknown) {
    if (!draftDocument.value) return;
    draftDocument.value = {
      ...draftDocument.value,
      content: updateSection(draftDocument.value.content, sectionName, value),
    };
  }

  function confirmSectionByName(sectionName: string) {
    if (!draftDocument.value) return;
    draftDocument.value = {
      ...draftDocument.value,
      content: confirmSectionUtil(draftDocument.value.content, sectionName),
    };
  }

  function confirmAll() {
    if (!draftDocument.value) return;
    draftDocument.value = {
      ...draftDocument.value,
      content: confirmAllSections(draftDocument.value.content),
    };
    toast.success('已确认全部内容');
  }

  function toggleSectionCollapse(sectionName: string) {
    collapsedSections.value = {
      ...collapsedSections.value,
      [sectionName]: !collapsedSections.value[sectionName],
    };
  }

  function toggleAllSections() {
    const allCollapsed = sections.value.every((s) => collapsedSections.value[s.name]);
    const next: Record<string, boolean> = {};
    for (const s of sections.value) {
      next[s.name] = !allCollapsed;
    }
    collapsedSections.value = next;
  }

  function scrollToSection(sectionName: string) {
    document.getElementById(`section-${sectionName}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  async function refreshFromServer() {
    try {
      const response = await documentsQuery.refetch();
      const doc = response.data?.items[activeDocTabIndex.value];
      if (doc) applyServerDocument(doc);
      toast.success('已刷新到最新版本');
    } catch (error) {
      toast.error('刷新失败', getErrorDescription(error, '请稍后重试。'));
    }
  }

  async function runQualityCheck(options: { openPanel?: boolean } = {}) {
    if (!activeDocument.value || !taskQuery.data.value) return;
    if (!(await ensureLatestDocumentSaved())) return;
    const openPanel = options.openPanel ?? true;
    try {
      const result = await qualityCheckMutation.mutateAsync();
      qualityResult.value = result;
      if (openPanel) {
        qualityPanelOpen.value = true;
        toast.success('导出前体检完成');
      }
      return result;
    } catch (error) {
      toast.error('导出前体检失败', getErrorDescription(error, '请稍后重试。'));
      return null;
    }
  }

  async function applyQualityFix(issue: QualityIssue) {
    if (!activeDocument.value) return;
    if (!(await ensureLatestDocumentSaved())) return;
    try {
      const updatedDocument = await qualityFixMutation.mutateAsync({
        section: issue.section,
        message: issue.message,
        suggestion: issue.suggestion,
      });
      applyServerDocument(updatedDocument);
      const result = await qualityCheckMutation.mutateAsync();
      qualityResult.value = result;
      qualityPanelOpen.value = true;
      toast.success('已生成待确认修订', '请检查对应 section 后再确认。');
    } catch (error) {
      toast.error('调整失败', getErrorDescription(error, '这个问题暂不支持自动调整。'));
    }
  }

  async function exportCurrentDocument(format: 'docx' | 'pptx' = 'docx') {
    if (!activeDocument.value || !taskQuery.data.value) return;
    exportMenuOpen.value = false;
    try {
      if (format === 'pptx') {
        await exportPptx(activeDocument.value.id, taskQuery.data.value.title);
        toast.success('课件已开始下载');
      } else {
        await exportDocx(activeDocument.value.id, taskQuery.data.value.title, selectedExportTemplateId.value || null);
        toast.success('Word 文档已开始下载');
      }
    } catch (error) {
      toast.error('导出失败', getErrorDescription(error, '请稍后重试。'));
    }
  }

  async function handleExport(format: 'docx' | 'pptx' = 'docx') {
    // PPTX 导出跳过质量检查，直接导出
    if (format === 'pptx') {
      await exportCurrentDocument('pptx');
      return;
    }
    const result = await runQualityCheck({ openPanel: false });
    if (!result) return;
    if (result.readiness === 'blocked') {
      qualityPanelOpen.value = true;
      toast.error('导出前还有阻断项', '请先处理体检中标出的关键问题。');
      return;
    }
    if (result.readiness === 'needs_fixes') {
      qualityPanelOpen.value = true;
      toast.info('导出前有提醒项', '你可以先处理，也可以确认后继续导出。');
      return;
    }
    await exportCurrentDocument('docx');
  }

  async function exportAfterQualityCheck() {
    qualityPanelOpen.value = false;
    if (!(await ensureLatestDocumentSaved())) return;
    await exportCurrentDocument();
  }

  function openExportPreview() {
    exportMenuOpen.value = false;
    exportPreviewOpen.value = true;
  }

  async function handleExportAll() {
    if (!taskQuery.data.value) return;
    if (!(await ensureLatestDocumentSaved())) return;
    exportMenuOpen.value = false;
    try {
      const docs = documentsQuery.data.value?.items ?? [];
      const items = docs.map((doc) => ({
        documentId: doc.id,
        title: `${taskQuery.data.value!.title}_${doc.doc_type === 'study_guide' ? '学案' : '教案'}`,
      }));
      await exportMultipleDocx(items);
      toast.success('全部文档已开始下载');
    } catch (error) {
      toast.error('导出失败', getErrorDescription(error, '请稍后重试。'));
    }
  }

  async function restoreSnapshot(snapshotId: string) {
    try {
      const updatedDocument = await restoreSnapshotMutation.mutateAsync(snapshotId);
      applyServerDocument(updatedDocument);
      if (historyOpen.value) void historyQuery.refetch();
      toast.success('已恢复历史版本');
    } catch (error) {
      toast.error('恢复失败', getErrorDescription(error, '请稍后重试。'));
    }
  }

  async function generateTeachingPackage() {
    if (!activeDocument.value || currentDocType.value !== 'lesson_plan') return;
    if (!(await ensureLatestDocumentSaved())) return;
    try {
      const result = await teachingPackageMutation.mutateAsync();
      teachingPackageResult.value = result;
      toast.success('上课包已整理', '学案、PPT 大纲和口播稿都已生成待确认草稿。');
    } catch (error) {
      toast.error('生成上课包失败', getErrorDescription(error, '请先确认教案核心内容。'));
    }
  }

  function togglePersonalAssetSelection(assetId: string) {
    if (selectedPersonalAssetIds.value.includes(assetId)) {
      selectedPersonalAssetIds.value = selectedPersonalAssetIds.value.filter((id) => id !== assetId);
      return;
    }
    selectedPersonalAssetIds.value = [...selectedPersonalAssetIds.value, assetId];
  }

  async function startGenerationWithPersonalAssets() {
    await startGeneration({
      usePersonalAssets: usePersonalAssetsForGeneration.value,
      personalAssetIds: selectedPersonalAssetIds.value,
    });
  }

  function handleKeydown(event: KeyboardEvent) {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 's') {
      event.preventDefault();
      void persistDocument({ attempt: 'manual' });
      return;
    }
    if (event.key === 'Escape') {
      historyOpen.value = false;
      exportMenuOpen.value = false;
      exportPreviewOpen.value = false;
    }
  }

  function syncOutlineForViewport() {
    if (typeof window === 'undefined') return;
    isMobileViewport.value = window.innerWidth < 720;
    if (window.innerWidth < 1100) outlineCollapsed.value = true;
  }

  function _generationOptionsFromRoute() {
    const useAssets = route.query.usePersonalAssets === '1' || route.query.usePersonalAssets === 'true';
    const rawIds = route.query.personalAssetIds;
    const idsText = Array.isArray(rawIds) ? rawIds.join(',') : rawIds || '';
    return {
      usePersonalAssets: useAssets,
      personalAssetIds: idsText.split(',').map((item) => item.trim()).filter(Boolean),
    };
  }

  onMounted(() => {
    syncOutlineForViewport();
    window.addEventListener('keydown', handleKeydown);
    window.addEventListener('resize', syncOutlineForViewport);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
  });

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeydown);
    window.removeEventListener('resize', syncOutlineForViewport);
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  });

  // Computed for template
  const hasPending = computed(() => sections.value.some((s) => s.status === 'pending'));
  const allCollapsed = computed(() => sections.value.length > 0 && sections.value.every((s) => collapsedSections.value[s.name]));
  const showInitialSkeleton = computed(() => {
    if (draftDocument.value) return false;
    if (taskQuery.isLoading.value || documentsQuery.isLoading.value) return true;
    return Boolean(taskQuery.data.value) && !documentsQuery.data.value;
  });
  const hasMultipleDocs = computed(() => (documentsQuery.data.value?.items.length ?? 0) > 1);

  return {
    router,
    taskQuery,
    documentsQuery,
    draftDocument,
    saveState,
    streamError,
    historyOpen,
    exportMenuOpen,
    exportPreviewOpen,
    qualityPanelOpen,
    qualityResult,
    qualityChecking: qualityCheckMutation.isPending,
    qualityFixing: qualityFixMutation.isPending,
    selectedExportTemplateId,
    schoolTemplatesQuery,
    assetRecommendationsQuery,
    usePersonalAssetsForGeneration,
    selectedPersonalAssetIds,
    teachingPackageResult,
    teachingPackageGenerating: teachingPackageMutation.isPending,
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
    runQualityCheck,
    applyQualityFix,
    exportAfterQualityCheck,
    generateTeachingPackage,
    startGenerationWithPersonalAssets,
    togglePersonalAssetSelection,
    openExportPreview,
    restoreSnapshot,
    confirmSectionByName,
    confirmAll,
    getSectionData,
    getSectionReferences,
    updateSectionData,
    toggleSectionCollapse,
    toggleAllSections,
  };
}
