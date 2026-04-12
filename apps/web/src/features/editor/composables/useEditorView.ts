import type { Block, BlockType, ContentDocument } from '@lessonpilot/shared-types';

import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useBillingDialogStore } from '@/app/stores/billing';
import { getBillingErrorDetail } from '@/features/billing/utils';
import {
  useDocumentHistory,
  useDocumentSnapshot,
  useRestoreSnapshotMutation,
  useStartDocumentAppendMutation,
  useStartDocumentRewriteMutation,
  useTaskDocuments,
  useUpdateDocumentMutation,
} from '@/features/editor/composables/useEditor';
import type { DocumentSnapshotRecord, LessonDocument } from '@/features/editor/types';
import { exportDocx, exportPdf } from '@/features/export/composables/useExport';
import {
  consumeAppendStream,
  consumeGenerationStream,
  consumeRewriteStream,
} from '@/features/generation/composables/useGeneration';
import { useSubscription } from '@/features/settings/composables/useAccount';
import { useStartGenerationMutation, useTask } from '@/features/task/composables/useTasks';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';
import {
  acceptPendingBlock,
  adjustBlockIndent,
  appendBlockToContainer,
  appendExistingBlockToContainer,
  canInsertChild,
  cloneContent,
  cloneSerializable,
  collectSections,
  convertBlockType,
  createBlock,
  deleteBlock,
  findBlockLocation,
  getBlockIndent,
  getConfirmedContent,
  insertExistingBlockAfter,
  moveBlock,
  reorderBlockBefore,
  rejectPendingBlock,
  updateBlock,
} from '@/shared/utils/content';

const DEFAULT_SECTION_TITLES = ['教学目标', '教学重难点', '导入环节', '新授环节', '练习巩固', '课堂小结'];

export function useEditorView() {
  const router = useRouter();
  const route = useRoute();
  const authStore = useAuthStore();
  const billingDialog = useBillingDialogStore();
  const toast = useToast();

  const taskId = computed(() => String(route.params.taskId ?? ''));
  const taskQuery = useTask(taskId.value);
  const documentsQuery = useTaskDocuments(taskId.value);
  const subscriptionQuery = useSubscription();
  const startGenerationMutation = useStartGenerationMutation(taskId.value);
  const draftDocument = ref<LessonDocument | null>(null);
  const saveState = ref<'saved' | 'dirty' | 'saving' | 'conflict'>('saved');
  const streamError = ref('');
  const initialGenerationTriggered = ref(false);
  const suppressAutosave = ref(false);
  const activeBlockId = ref<string | null>(null);
  const openMenuBlockId = ref<string | null>(null);
  const visibleSectionId = ref<string | null>(null);
  const historyOpen = ref(false);
  const exportMenuOpen = ref(false);
  const exportPreviewOpen = ref(false);
  const outlineCollapsed = ref(typeof window !== 'undefined' ? window.innerWidth < 1100 : false);
  const isMobileViewport = ref(typeof window !== 'undefined' ? window.innerWidth < 720 : false);
  const selectedSnapshotId = ref('');
  const appendComposerOpen = ref(false);
  const appendInstruction = ref('');
  const notice = reactive<{
    text: string;
    tone: 'success' | 'info';
  }>({
    text: '',
    tone: 'success',
  });
  const generationProgress = reactive({
    isGenerating: false,
    completed: 0,
    total: 0,
    currentSection: '',
    currentSectionId: null as string | null,
  });
  const rewriteState = reactive<{
    isRewriting: boolean;
    targetBlockId: string | null;
    action: 'rewrite' | 'polish' | 'expand';
  }>({
    isRewriting: false,
    targetBlockId: null,
    action: 'rewrite',
  });
  const appendState = reactive({
    isAppending: false,
    sectionId: null as string | null,
    sectionTitle: '',
  });

  const startRewriteMutation = useStartDocumentRewriteMutation(() => draftDocument.value?.id ?? '');
  const startAppendMutation = useStartDocumentAppendMutation(() => draftDocument.value?.id ?? '');

  let saveTimer: number | undefined;
  let noticeTimer: number | undefined;
  let sectionObserver: IntersectionObserver | null = null;
  const sectionElements = new Map<string, HTMLElement>();

  const primaryDocument = computed(() => documentsQuery.data.value?.items[0] ?? null);
  const currentDocumentId = computed(() => draftDocument.value?.id ?? primaryDocument.value?.id ?? '');
  const sections = computed(() => (draftDocument.value ? collectSections(draftDocument.value.content) : []));
  const updateDocumentMutation = useUpdateDocumentMutation(
    () => draftDocument.value?.id ?? '',
    () => taskId.value,
  );
  const historyEnabled = computed(() => historyOpen.value && Boolean(currentDocumentId.value));
  const snapshotEnabled = computed(() => historyEnabled.value && Boolean(selectedSnapshotId.value));
  const historyQuery = useDocumentHistory(currentDocumentId, historyEnabled);
  const snapshotQuery = useDocumentSnapshot(currentDocumentId, selectedSnapshotId, snapshotEnabled);
  const restoreSnapshotMutation = useRestoreSnapshotMutation(
    () => currentDocumentId.value,
    () => taskId.value,
  );

  const previewSnapshot = computed<DocumentSnapshotRecord | null>(() => snapshotQuery.data.value ?? null);
  const currentSectionId = computed(() => {
    if (draftDocument.value && activeBlockId.value) {
      const location = findBlockLocation(draftDocument.value.content, activeBlockId.value);
      if (location?.sectionId) {
        return location.sectionId;
      }
    }

    return visibleSectionId.value ?? sections.value[0]?.id ?? null;
  });
  const currentSectionTitle = computed(
    () => sections.value.find((section) => section.id === currentSectionId.value)?.title ?? '',
  );
  const highlightedSectionId = computed(
    () => generationProgress.currentSectionId ?? currentSectionId.value,
  );
  const confirmedPreviewBlocks = computed(() =>
    draftDocument.value ? getConfirmedContent(draftDocument.value.content).blocks : [],
  );
  const showInitialSkeleton = computed(() => {
    if (draftDocument.value) {
      return false;
    }

    if (taskQuery.isLoading.value || documentsQuery.isLoading.value) {
      return true;
    }

    return Boolean(taskQuery.data.value) && !documentsQuery.data.value;
  });
  const skeletonSectionTitles = computed(() => {
    const titles = sections.value.map((section) => section.title);
    return titles.length ? titles : DEFAULT_SECTION_TITLES;
  });

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
        saveTimer = undefined;
        void persistDocument();
      }, 700);
    },
    { deep: true },
  );

  watch(
    () => historyQuery.data.value?.items,
    (items) => {
      if (!historyOpen.value || !items?.length) {
        return;
      }

      if (!selectedSnapshotId.value || !items.some((item) => item.id === selectedSnapshotId.value)) {
        selectedSnapshotId.value = items[0].id;
      }
    },
    { immediate: true },
  );

  watch(historyOpen, (open) => {
    if (!open) {
      selectedSnapshotId.value = '';
    }
  });

  watch(
    () => historyQuery.error.value,
    (error) => {
      if (!error) {
        return;
      }
      if (handleBillingError(error, '版本历史需要专业版', '版本历史为专业版能力，请升级后继续使用。')) {
        historyOpen.value = false;
      }
    },
  );

  watch(
    sections,
    () => {
      if (!visibleSectionId.value) {
        visibleSectionId.value = sections.value[0]?.id ?? null;
      }
      void refreshSectionObserver();
    },
    { deep: true },
  );

  function flashNotice(text: string, tone: 'success' | 'info' = 'success') {
    notice.text = text;
    notice.tone = tone;
    if (noticeTimer) {
      window.clearTimeout(noticeTimer);
    }
    noticeTimer = window.setTimeout(() => {
      notice.text = '';
    }, 3200);
  }

  function openUpgradeDialog(title: string, description: string) {
    billingDialog.openDialog({
      reason: 'plan_required',
      title,
      description,
    });
  }

  function hasProfessionalEntitlement(
    entitlement: 'ai_rewrite' | 'ai_append' | 'section_regenerate' | 'pdf_export' | 'version_history',
  ) {
    const entitlements = subscriptionQuery.data.value?.entitlements;
    if (!entitlements) {
      return true;
    }
    return Boolean(entitlements[entitlement]);
  }

  function handleBillingError(error: unknown, title: string, description: string): boolean {
    const billingError = getBillingErrorDetail(error);
    if (!billingError) {
      return false;
    }
    openUpgradeDialog(title, billingError.message || description);
    return true;
  }

  function focusEditableElement(element: HTMLElement | null) {
    if (!element) {
      return;
    }
    element.focus();
    if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
      const length = element.value.length;
      element.setSelectionRange(length, length);
      return;
    }
    const selection = window.getSelection();
    if (!selection) {
      return;
    }
    const range = document.createRange();
    range.selectNodeContents(element);
    range.collapse(false);
    selection.removeAllRanges();
    selection.addRange(range);
  }

  function requestBlockFocus(blockId: string, listItemIndex?: number) {
    void nextTick(() => {
      const escapedBlockId =
        typeof CSS !== 'undefined' && typeof CSS.escape === 'function' ? CSS.escape(blockId) : blockId;
      const target =
        listItemIndex === undefined
          ? document.querySelector<HTMLElement>(`[data-block-id="${escapedBlockId}"] .ProseMirror`)
          : document.querySelector<HTMLElement>(
              `[data-block-id="${escapedBlockId}"] [data-list-item-index="${listItemIndex}"]`,
            );
      focusEditableElement(target);
    });
  }

  function destroySectionObserver() {
    if (sectionObserver) {
      sectionObserver.disconnect();
      sectionObserver = null;
    }
  }

  async function refreshSectionObserver() {
    await nextTick();

    if (typeof window === 'undefined' || typeof IntersectionObserver === 'undefined') {
      return;
    }

    destroySectionObserver();
    sectionObserver = new IntersectionObserver(
      (entries) => {
        const visibleEntries = entries
          .filter((entry) => entry.isIntersecting)
          .sort((left, right) => right.intersectionRatio - left.intersectionRatio);

        const activeTarget = visibleEntries[0]?.target;
        const sectionId = activeTarget instanceof HTMLElement ? activeTarget.dataset.sectionId : null;
        if (sectionId) {
          visibleSectionId.value = sectionId;
        }
      },
      {
        rootMargin: '-18% 0px -58% 0px',
        threshold: [0.2, 0.45, 0.7],
      },
    );

    sectionElements.forEach((element) => {
      sectionObserver?.observe(element);
    });
  }

  function setSectionElement(sectionId: string, element: Element | null) {
    const previous = sectionElements.get(sectionId);
    if (previous && sectionObserver) {
      sectionObserver.unobserve(previous);
    }

    if (element instanceof HTMLElement) {
      sectionElements.set(sectionId, element);
      sectionObserver?.observe(element);
      return;
    }

    sectionElements.delete(sectionId);
  }

  function syncOutlineForViewport() {
    if (typeof window === 'undefined') {
      return;
    }
    isMobileViewport.value = window.innerWidth < 720;
    if (window.innerWidth < 1100) {
      outlineCollapsed.value = true;
    }
  }

  function applyServerDocument(document: LessonDocument) {
    const previousVisibleSectionId = visibleSectionId.value;
    const nextSections = collectSections(document.content);
    suppressAutosave.value = true;
    draftDocument.value = cloneSerializable(document);
    saveState.value = 'saved';
    visibleSectionId.value =
      nextSections.find((section) => section.id === previousVisibleSectionId)?.id ??
      nextSections[0]?.id ??
      null;
    nextTick(() => {
      suppressAutosave.value = false;
      void refreshSectionObserver();
    });
  }

  async function persistDocument(): Promise<boolean> {
    if (!draftDocument.value) {
      return false;
    }

    saveState.value = 'saving';
    try {
      const updatedDocument = await updateDocumentMutation.mutateAsync({
        version: draftDocument.value.version,
        content: draftDocument.value.content,
      });
      applyServerDocument(updatedDocument);
      return true;
    } catch {
      saveState.value = 'conflict';
      return false;
    }
  }

  async function ensureLatestDocumentSaved(): Promise<boolean> {
    if (!draftDocument.value) {
      return false;
    }

    if (saveTimer) {
      window.clearTimeout(saveTimer);
      saveTimer = undefined;
    }

    if (saveState.value === 'dirty' || saveState.value === 'saving') {
      const saved = await persistDocument();
      if (!saved) {
        streamError.value = '请先处理保存冲突，再继续当前操作。';
        return false;
      }
    }

    if (saveState.value === 'conflict') {
      streamError.value = '请先刷新最新版本，再继续当前操作。';
      return false;
    }

    return true;
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

  function handleBlockUpdate(nextBlock: Block) {
    if (!draftDocument.value) {
      return;
    }
    updateContent(updateBlock(draftDocument.value.content, nextBlock.id, () => nextBlock));
  }

  function handleAppendToContainer(
    parentId: string,
    type: 'paragraph' | 'list' | 'teaching_step' | 'exercise_group' | 'choice_question' | 'fill_blank_question' | 'short_answer_question',
  ) {
    if (!draftDocument.value) {
      return;
    }
    updateContent(appendBlockToContainer(draftDocument.value.content, parentId, type));
  }

  function handleMove(blockId: string, direction: 'up' | 'down') {
    if (!draftDocument.value) {
      return;
    }
    updateContent(moveBlock(draftDocument.value.content, blockId, direction));
  }

  function handleDelete(blockId: string) {
    if (!draftDocument.value) {
      return;
    }
    openMenuBlockId.value = null;
    if (activeBlockId.value === blockId) {
      activeBlockId.value = null;
    }
    updateContent(deleteBlock(draftDocument.value.content, blockId));
  }

  function handleConvert(blockId: string, targetType: BlockType) {
    if (!draftDocument.value) {
      return;
    }
    openMenuBlockId.value = null;
    updateContent(convertBlockType(draftDocument.value.content, blockId, targetType));
  }

  function handleReorder(draggedId: string, targetId: string, parentId: string) {
    if (!draftDocument.value) {
      return;
    }
    updateContent(reorderBlockBefore(draftDocument.value.content, draggedId, targetId, parentId));
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

  function handleIndentBlock(blockId: string, direction: 'in' | 'out') {
    if (!draftDocument.value) {
      return;
    }
    updateContent(adjustBlockIndent(draftDocument.value.content, blockId, direction));
    requestBlockFocus(blockId);
  }

  function handleInsertParagraphAfter(blockId: string) {
    if (!draftDocument.value) {
      return;
    }
    const location = findBlockLocation(draftDocument.value.content, blockId);
    if (!location || !canInsertChild(location.parentType, 'paragraph')) {
      return;
    }

    const paragraph = createBlock('paragraph') as Extract<Block, { type: 'paragraph' }>;
    if (location.block.type === 'paragraph' || location.block.type === 'list') {
      paragraph.indent = getBlockIndent(location.block);
    }
    updateContent(insertExistingBlockAfter(draftDocument.value.content, blockId, paragraph));
    activeBlockId.value = paragraph.id;
    requestBlockFocus(paragraph.id);
  }

  function handleInsertListItem(blockId: string, index: number) {
    if (!draftDocument.value) {
      return;
    }
    updateContent(
      updateBlock(draftDocument.value.content, blockId, (block) => {
        if (block.type !== 'list') {
          return block;
        }
        const items = [...block.items];
        items.splice(index + 1, 0, '');
        return { ...block, items };
      }),
    );
    activeBlockId.value = blockId;
    requestBlockFocus(blockId, index + 1);
  }

  function handleExitListToParagraph(blockId: string, index: number) {
    if (!draftDocument.value) {
      return;
    }

    const nextContent = cloneContent(draftDocument.value.content);
    const location = findBlockLocation(nextContent, blockId);
    if (!location || location.block.type !== 'list') {
      return;
    }

    const paragraph = createBlock('paragraph') as Extract<Block, { type: 'paragraph' }>;
    paragraph.indent = getBlockIndent(location.block);
    const nextItems = location.block.items.filter((_, itemIndex) => itemIndex !== index);

    if (nextItems.length) {
      location.block.items = nextItems;
      location.siblings.splice(location.index + 1, 0, paragraph);
    } else {
      location.siblings.splice(location.index, 1, paragraph);
    }

    updateContent(nextContent);
    activeBlockId.value = paragraph.id;
    requestBlockFocus(paragraph.id);
  }

  function scrollToSection(sectionId: string) {
    visibleSectionId.value = sectionId;
    document.getElementById(`section-${sectionId}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function isSectionShowingSkeleton(sectionId: string, childrenCount: number): boolean {
    return generationProgress.isGenerating && childrenCount === 0 && Boolean(sectionId);
  }

  async function startGeneration(sectionId?: string) {
    if (!authStore.token) {
      return;
    }
    if (sectionId && !hasProfessionalEntitlement('section_regenerate')) {
      openUpgradeDialog('章节重新生成需要专业版', '章节重新生成为专业版能力，请升级后继续使用。');
      return;
    }
    if (!(await ensureLatestDocumentSaved())) {
      return;
    }

    streamError.value = '';
    generationProgress.isGenerating = true;
    generationProgress.completed = 0;
    generationProgress.total = sections.value.length;
    generationProgress.currentSection = '';
    generationProgress.currentSectionId = sectionId ?? null;

    try {
      const response = await startGenerationMutation.mutateAsync(sectionId);
      await consumeGenerationStream(response.stream_url, authStore.token, {
        onEvent(event, payload) {
          if (event === 'status') {
            const state = (payload as { state: string }).state;
            generationProgress.isGenerating = state === 'generating';
            if (state === 'ready') {
              generationProgress.currentSectionId = null;
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
            generationProgress.currentSectionId = progress.section_id;
            visibleSectionId.value = progress.section_id;
          }

          if (event === 'document') {
            applyServerDocument(payload as LessonDocument);
          }

          if (event === 'done') {
            generationProgress.isGenerating = false;
            generationProgress.currentSectionId = null;
            void taskQuery.refetch();
            void documentsQuery.refetch();
            if (historyOpen.value) {
              void historyQuery.refetch();
            }
            flashNotice(sectionId ? '本节 AI 内容已生成，等待你确认。' : '教案已生成，你可以开始编辑。');
          }

          if (event === 'error') {
            streamError.value = (payload as { message: string }).message;
            generationProgress.isGenerating = false;
            generationProgress.currentSectionId = null;
          }
        },
      });
    } catch (error) {
      if (handleBillingError(error, '章节重新生成需要专业版', '章节重新生成为专业版能力，请升级后继续使用。')) {
        generationProgress.isGenerating = false;
        generationProgress.currentSectionId = null;
        return;
      }
      streamError.value = '生成流打开失败，请稍后重试。';
      generationProgress.isGenerating = false;
      generationProgress.currentSectionId = null;
    }
  }

  async function startRewrite(payload: {
    mode: 'block' | 'selection';
    targetBlockId: string;
    action: 'rewrite' | 'polish' | 'expand';
    selectionText?: string;
  }) {
    if (!authStore.token || !draftDocument.value) {
      return;
    }
    if (!hasProfessionalEntitlement('ai_rewrite')) {
      openUpgradeDialog('局部 AI 重写需要专业版', '局部 AI 重写与文本润色为专业版能力，请升级后继续使用。');
      return;
    }
    if (!(await ensureLatestDocumentSaved())) {
      return;
    }

    streamError.value = '';
    rewriteState.isRewriting = true;
    rewriteState.targetBlockId = payload.targetBlockId;
    rewriteState.action = payload.action;
    openMenuBlockId.value = null;

    try {
      const response = await startRewriteMutation.mutateAsync({
        document_version: draftDocument.value.version,
        mode: payload.mode,
        target_block_id: payload.targetBlockId,
        action: payload.action,
        selection_text: payload.selectionText ?? null,
      });
      await consumeRewriteStream(response.stream_url, authStore.token, {
        onEvent(event, eventPayload) {
          if (event === 'document') {
            applyServerDocument(eventPayload as LessonDocument);
          }
          if (event === 'done') {
            rewriteState.isRewriting = false;
            rewriteState.targetBlockId = null;
            void documentsQuery.refetch();
            if (historyOpen.value) {
              void historyQuery.refetch();
            }
            flashNotice('AI 建议已生成，等待你确认。', 'info');
          }
          if (event === 'error') {
            streamError.value = (eventPayload as { message: string }).message;
            rewriteState.isRewriting = false;
            rewriteState.targetBlockId = null;
          }
        },
      });
    } catch (error) {
      if (handleBillingError(error, '局部 AI 重写需要专业版', '局部 AI 重写与文本润色为专业版能力，请升级后继续使用。')) {
        rewriteState.isRewriting = false;
        rewriteState.targetBlockId = null;
        return;
      }
      streamError.value = 'AI 重写失败，请稍后再试。';
      rewriteState.isRewriting = false;
      rewriteState.targetBlockId = null;
    }
  }

  async function startAppend() {
    if (!authStore.token || !draftDocument.value || !currentSectionId.value || !appendInstruction.value.trim()) {
      return;
    }
    if (!hasProfessionalEntitlement('ai_append')) {
      openUpgradeDialog('AI 补充内容需要专业版', 'AI 补充内容为专业版能力，请升级后继续使用。');
      return;
    }
    if (!(await ensureLatestDocumentSaved())) {
      return;
    }

    streamError.value = '';
    appendState.isAppending = true;
    appendState.sectionId = currentSectionId.value;
    appendState.sectionTitle = currentSectionTitle.value;

    try {
      const response = await startAppendMutation.mutateAsync({
        document_version: draftDocument.value.version,
        section_id: currentSectionId.value,
        instruction: appendInstruction.value.trim(),
      });
      await consumeAppendStream(response.stream_url, authStore.token, {
        onEvent(event, eventPayload) {
          if (event === 'document') {
            applyServerDocument(eventPayload as LessonDocument);
          }
          if (event === 'done') {
            appendState.isAppending = false;
            appendComposerOpen.value = false;
            appendInstruction.value = '';
            void documentsQuery.refetch();
            if (historyOpen.value) {
              void historyQuery.refetch();
            }
            flashNotice(`AI 已为 ${appendState.sectionTitle || '当前章节'} 补充内容。`, 'info');
          }
          if (event === 'error') {
            streamError.value = (eventPayload as { message: string }).message;
            appendState.isAppending = false;
          }
        },
      });
    } catch (error) {
      if (handleBillingError(error, 'AI 补充内容需要专业版', 'AI 补充内容为专业版能力，请升级后继续使用。')) {
        appendState.isAppending = false;
        return;
      }
      streamError.value = 'AI 补充内容失败，请稍后再试。';
      appendState.isAppending = false;
    }
  }

  async function refreshFromServer() {
    try {
      const response = await documentsQuery.refetch();
      const document = response.data?.items[0];
      if (document) {
        applyServerDocument(document);
      }
      toast.success('已刷新到最新版本');
    } catch (error) {
      streamError.value = '刷新最新版本失败，请稍后重试。';
      toast.error('刷新失败', getErrorDescription(error, '请稍后重试。'));
    }
  }

  async function handleExport(format: 'docx' | 'pdf') {
    if (!draftDocument.value || !taskQuery.data.value) {
      return;
    }
    if (format === 'pdf' && !hasProfessionalEntitlement('pdf_export')) {
      openUpgradeDialog('PDF 导出需要专业版', 'PDF 导出为专业版能力，请升级后继续使用。');
      return;
    }
    if (!(await ensureLatestDocumentSaved())) {
      return;
    }
    exportMenuOpen.value = false;
    try {
      if (format === 'docx') {
        await exportDocx(draftDocument.value.id, taskQuery.data.value.title);
        toast.success('Word 文档已开始下载');
        return;
      }
      await exportPdf(draftDocument.value.id, taskQuery.data.value.title);
      toast.success('PDF 文档已开始下载');
    } catch (error) {
      if (handleBillingError(error, 'PDF 导出需要专业版', 'PDF 导出为专业版能力，请升级后继续使用。')) {
        return;
      }
      toast.error('导出失败', getErrorDescription(error, '请稍后重试。'));
    }
  }

  function openExportPreview() {
    exportMenuOpen.value = false;
    exportPreviewOpen.value = true;
  }

  async function restoreSnapshot(snapshotId: string) {
    if (!hasProfessionalEntitlement('version_history')) {
      openUpgradeDialog('版本历史需要专业版', '版本预览与恢复为专业版能力，请升级后继续使用。');
      return;
    }
    try {
      const updatedDocument = await restoreSnapshotMutation.mutateAsync(snapshotId);
      applyServerDocument(updatedDocument);
      if (historyOpen.value) {
        void historyQuery.refetch();
      }
      flashNotice('已恢复历史版本，并创建了一个新版本。', 'info');
      toast.success('已恢复历史版本');
    } catch (error) {
      toast.error('恢复历史版本失败', getErrorDescription(error, '请稍后重试。'));
    }
  }

  function handleInsertAfter(type: 'paragraph' | 'list') {
    if (!draftDocument.value || !activeBlockId.value) {
      return;
    }
    const location = findBlockLocation(draftDocument.value.content, activeBlockId.value);
    if (!location || !canInsertChild(location.parentType, type)) {
      return;
    }
    const nextBlock = createBlock(type);
    if ((type === 'paragraph' || type === 'list') && (location.block.type === 'paragraph' || location.block.type === 'list')) {
      nextBlock.indent = getBlockIndent(location.block);
    }
    updateContent(insertExistingBlockAfter(draftDocument.value.content, activeBlockId.value, nextBlock));
    activeBlockId.value = nextBlock.id;
    requestBlockFocus(nextBlock.id, type === 'list' ? 0 : undefined);
  }

  function handleBottomAddParagraph() {
    if (!draftDocument.value || !currentSectionId.value) {
      return;
    }
    const paragraph = createBlock('paragraph');
    updateContent(appendExistingBlockToContainer(draftDocument.value.content, currentSectionId.value, paragraph));
    activeBlockId.value = paragraph.id;
    requestBlockFocus(paragraph.id);
  }

  function handleBottomAddExercise() {
    if (!draftDocument.value || !currentSectionId.value) {
      return;
    }
    const exerciseGroup = createBlock('exercise_group');
    updateContent(appendExistingBlockToContainer(draftDocument.value.content, currentSectionId.value, exerciseGroup));
    activeBlockId.value = exerciseGroup.id;
  }

  function toggleAppendComposer() {
    appendComposerOpen.value = !appendComposerOpen.value;
  }

  function cancelAppendComposer() {
    appendComposerOpen.value = false;
    appendInstruction.value = '';
  }

  function openHistoryDrawer() {
    if (!hasProfessionalEntitlement('version_history')) {
      openUpgradeDialog('版本历史需要专业版', '版本历史为专业版能力，请升级后继续使用。');
      return;
    }
    historyOpen.value = true;
  }

  function handleKeydown(event: KeyboardEvent) {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 's') {
      event.preventDefault();
      void persistDocument();
      return;
    }

    if (event.key === 'Escape') {
      historyOpen.value = false;
      openMenuBlockId.value = null;
      exportMenuOpen.value = false;
      exportPreviewOpen.value = false;
      appendComposerOpen.value = false;
      return;
    }

    if (!draftDocument.value || !activeBlockId.value) {
      return;
    }

    if (event.altKey && !event.shiftKey && event.key === 'ArrowUp') {
      event.preventDefault();
      handleMove(activeBlockId.value, 'up');
    }

    if (event.altKey && !event.shiftKey && event.key === 'ArrowDown') {
      event.preventDefault();
      handleMove(activeBlockId.value, 'down');
    }

    if (event.altKey && event.shiftKey && event.key.toLowerCase() === 'p') {
      event.preventDefault();
      handleInsertAfter('paragraph');
    }

    if (event.altKey && event.shiftKey && event.key.toLowerCase() === 'l') {
      event.preventDefault();
      handleInsertAfter('list');
    }
  }

  onMounted(() => {
    syncOutlineForViewport();
    window.addEventListener('keydown', handleKeydown);
    window.addEventListener('resize', syncOutlineForViewport);
  });

  onBeforeUnmount(() => {
    window.removeEventListener('keydown', handleKeydown);
    window.removeEventListener('resize', syncOutlineForViewport);
    if (saveTimer) {
      window.clearTimeout(saveTimer);
    }
    if (noticeTimer) {
      window.clearTimeout(noticeTimer);
    }
    destroySectionObserver();
  });

  return {
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
  };
}
