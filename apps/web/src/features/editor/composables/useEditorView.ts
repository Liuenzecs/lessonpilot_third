/**
 * 编辑器主 composable。
 * 组合 useAutoSave、useEditorGeneration、useEditorRewrite，
 * 管理文档加载、Tab 切换、section 状态。
 */
import type { DocumentContent, SectionInfo } from '@lessonpilot/shared-types';
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import {
  useDocumentHistory,
  useDocumentSnapshot,
  useRestoreSnapshotMutation,
  useTaskDocuments,
} from '@/features/editor/composables/useEditor';
import { useAutoSave } from '@/features/editor/composables/useAutoSave';
import { useEditorGeneration } from '@/features/editor/composables/useEditorGeneration';
import { useEditorRewrite } from '@/features/editor/composables/useEditorRewrite';
import type { DocumentSnapshotRecord, LessonDocument } from '@/features/editor/types';
import { exportDocx, exportMultipleDocx } from '@/features/export/composables/useExport';
import { useTask } from '@/features/task/composables/useTasks';
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
  const outlineCollapsed = ref(typeof window !== 'undefined' ? window.innerWidth < 1100 : false);
  const isMobileViewport = ref(typeof window !== 'undefined' ? window.innerWidth < 720 : false);
  const selectedSnapshotId = ref('');
  const collapsedSections = ref<Record<string, boolean>>({});
  const activeDocTabIndex = ref(0);

  const primaryDocument = computed(() => documentsQuery.data.value?.items[0] ?? null);
  const secondaryDocument = computed(() => documentsQuery.data.value?.items[1] ?? null);

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
  const previewSnapshot = computed<DocumentSnapshotRecord | null>(() => snapshotQuery.data.value ?? null);

  // Flash notice
  const notice = reactive<{ text: string; tone: 'success' | 'info' }>({ text: '', tone: 'success' });
  let noticeTimer: number | undefined;

  function flashNotice(text: string, tone: 'success' | 'info' = 'success') {
    notice.text = text;
    notice.tone = tone;
    if (noticeTimer) window.clearTimeout(noticeTimer);
    noticeTimer = window.setTimeout(() => { notice.text = ''; }, 3200);
  }

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
        void startGeneration();
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

  async function handleExport() {
    if (!activeDocument.value || !taskQuery.data.value) return;
    if (!(await ensureLatestDocumentSaved())) return;
    exportMenuOpen.value = false;
    try {
      await exportDocx(activeDocument.value.id, taskQuery.data.value.title);
      toast.success('Word 文档已开始下载');
    } catch (error) {
      toast.error('导出失败', getErrorDescription(error, '请稍后重试。'));
    }
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
    if (noticeTimer) window.clearTimeout(noticeTimer);
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
    getSectionReferences,
    updateSectionData,
    toggleSectionCollapse,
    toggleAllSections,
  };
}
