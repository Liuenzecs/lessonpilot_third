/**
 * AI 生成流式消费 composable。
 * 从 useEditorView 中提取的 AI 生成逻辑。
 */
import type { Ref } from 'vue';
import { reactive } from 'vue';

import type { LessonDocument } from '@/features/editor/types';
import { consumeGenerationStream } from '@/features/generation/composables/useGeneration';
import { useStartGenerationMutation, useTask } from '@/features/task/composables/useTasks';
import { useAuthStore } from '@/app/stores/auth';
import { useToast } from '@/shared/composables/useToast';

interface UseEditorGenerationOptions {
  taskId: string;
  draftDocument: Ref<LessonDocument | null>;
  ensureLatestDocumentSaved: () => Promise<boolean>;
  onApplyServerDocument: (doc: LessonDocument) => void;
  onRefetch: () => void;
  getSectionsCount: () => number;
}

export function useEditorGeneration(options: UseEditorGenerationOptions) {
  const {
    taskId,
    draftDocument,
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
    abortController = new AbortController();

    try {
      const response = await startGenerationMutation.mutateAsync(sectionName);
      await consumeGenerationStream(
        response.stream_url,
        authStore.token,
        {
          onStatus(payload) {
            if (payload.status === 'ready') {
              generationProgress.currentSectionName = null;
            }
          },
          onProgress(payload) {
            generationProgress.total = Math.max(generationProgress.total, 1);
            if (payload.doc_type) {
              generationProgress.docType = payload.doc_type;
            }
          },
          onSectionStart(payload) {
            generationProgress.currentSection = payload.title;
            generationProgress.currentSectionName = payload.section_name;
            generationProgress.docType = payload.doc_type;
          },
          onSectionDelta(payload) {
            generationProgress.streamingText += payload.text;
          },
          onSectionComplete() {
            generationProgress.completed++;
          },
          onDocument(payload) {
            onApplyServerDocument(payload as unknown as LessonDocument);
            generationProgress.streamingText = '';
          },
          onDone() {
            generationProgress.isGenerating = false;
            generationProgress.currentSectionName = null;
            generationProgress.streamingText = '';
            abortController = null;
            onRefetch();
            toast.success(sectionName ? '本节内容已生成' : '教案已生成，你可以开始编辑。');
          },
          onError(payload) {
            generationProgress.streamingText = '';
            generationProgress.isGenerating = false;
            generationProgress.currentSectionName = null;
            abortController = null;
            toast.error('生成失败', '内容生成出现问题，请稍后重试。');
          },
        },
        abortController.signal,
      );
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        generationProgress.isGenerating = false;
        generationProgress.streamingText = '';
        abortController = null;
        toast.info('已停止生成。');
        return;
      }
      generationProgress.isGenerating = false;
      generationProgress.currentSectionName = null;
      generationProgress.streamingText = '';
      abortController = null;
      toast.error('生成失败', '生成流打开失败，请稍后重试。');
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
