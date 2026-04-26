import { reactive } from 'vue';

import type { LessonDocument } from '@/features/editor/types';
import type { RagStatusInfo } from '@/features/generation/composables/useGeneration';
import { consumeSectionStream } from '@/features/generation/composables/useGeneration';
import { useStartGenerationMutation } from '@/features/task/composables/useTasks';
import { useAuthStore } from '@/app/stores/auth';
import { useToast } from '@/shared/composables/useToast';

interface UseEditorGenerationOptions {
  taskId: string;
  ensureLatestDocumentSaved: () => Promise<boolean>;
  onApplyServerDocument: (doc: LessonDocument) => void;
  onRefetch: () => void;
  getSectionsCount: () => number;
}

export function useEditorGeneration(options: UseEditorGenerationOptions) {
  const {
    taskId,
    ensureLatestDocumentSaved,
    onApplyServerDocument,
    onRefetch,
    getSectionsCount,
  } = options;

  const authStore = useAuthStore();
  const toast = useToast();
  const startGenerationMutation = useStartGenerationMutation(taskId);

  const generationProgress = reactive({
    isGenerating: false,
    completed: 0,
    total: 0,
    currentSection: '',
    currentSectionName: null as string | null,
    streamingText: '',
    docType: '',
    ragStatus: null as RagStatusInfo | null,
  });

  let abortController: AbortController | null = null;

  async function startGeneration(sectionName?: string) {
    if (!authStore.token) return;
    if (!(await ensureLatestDocumentSaved())) return;

    generationProgress.isGenerating = true;
    generationProgress.completed = 0;
    generationProgress.total = getSectionsCount();
    generationProgress.currentSection = '';
    generationProgress.currentSectionName = sectionName ?? null;
    generationProgress.streamingText = '';
    generationProgress.docType = '';
    generationProgress.ragStatus = null;
    abortController = new AbortController();

    try {
      const response = await startGenerationMutation.mutateAsync(sectionName);
      await consumeSectionStream(
        response.stream_url,
        authStore.token,
        {
          onStatus(payload) {
            if (payload.status === 'ready') {
              generationProgress.currentSectionName = null;
            }
          },
          onProgress(payload) {
            if (typeof payload.total === 'number') {
              generationProgress.total = payload.total;
            } else {
              generationProgress.total = Math.max(generationProgress.total, 1);
            }
            if (payload.doc_type) {
              generationProgress.docType = payload.doc_type;
            }
          },
          onSectionStart(payload) {
            generationProgress.currentSection = payload.title;
            generationProgress.currentSectionName = payload.section_name;
            generationProgress.docType = payload.doc_type ?? generationProgress.docType;
          },
          onSectionDelta(payload) {
            generationProgress.streamingText += payload.delta ?? payload.text ?? '';
          },
          onSectionDocument(payload) {
            onApplyServerDocument(payload);
            generationProgress.streamingText = '';
          },
          onSectionDone() {
            generationProgress.completed++;
          },
          onRagStatus(payload) {
            generationProgress.ragStatus = payload;
          },
          onWarning(payload) {
            toast.info('整理提醒', payload.message);
          },
          onDocumentDone() {
            generationProgress.isGenerating = false;
            generationProgress.currentSectionName = null;
            generationProgress.streamingText = '';
            abortController = null;
            onRefetch();
            toast.success(sectionName ? '本节内容已写入草稿' : '初稿已整理完成，你可以开始编辑。');
          },
          onError() {
            generationProgress.streamingText = '';
            generationProgress.isGenerating = false;
            generationProgress.currentSectionName = null;
            abortController = null;
            toast.error('整理失败', '内容整理出现问题，请稍后重试。');
          },
        },
        abortController.signal,
      );
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        generationProgress.isGenerating = false;
        generationProgress.streamingText = '';
        abortController = null;
        toast.info('已停止整理。');
        return;
      }
      generationProgress.isGenerating = false;
      generationProgress.currentSectionName = null;
      generationProgress.streamingText = '';
      abortController = null;
      toast.error('整理失败', '整理通道打开失败，请稍后重试。');
    }
  }

  function stopGeneration() {
    if (abortController) {
      abortController.abort();
    }
  }

  return {
    generationProgress,
    startGeneration,
    stopGeneration,
  };
}
