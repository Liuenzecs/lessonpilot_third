/**
 * Section 级 AI 重写 composable。
 * 处理 rewrite/expand/simplify 操作，消费新的流式 SSE 事件。
 */
import type { Ref } from 'vue';
import { reactive } from 'vue';

import { useStartDocumentRewriteMutation } from '@/features/editor/composables/useEditor';
import type { LessonDocument } from '@/features/editor/types';
import { consumeSectionStream } from '@/features/generation/composables/useGeneration';
import { useAuthStore } from '@/app/stores/auth';
import { useToast } from '@/shared/composables/useToast';

interface UseEditorRewriteOptions {
  draftDocument: Ref<LessonDocument | null>;
  streamError: Ref<string>;
  ensureLatestDocumentSaved: () => Promise<boolean>;
  onApplyServerDocument: (doc: LessonDocument) => void;
  onRefetch: () => void;
}

export function useEditorRewrite(options: UseEditorRewriteOptions) {
  const {
    draftDocument,
    streamError,
    ensureLatestDocumentSaved,
    onApplyServerDocument,
    onRefetch,
  } = options;

  const authStore = useAuthStore();
  const toast = useToast();
  const startRewriteMutation = useStartDocumentRewriteMutation(() => draftDocument.value?.id ?? '');

  const rewriteState = reactive({
    isRewriting: false,
    sectionName: null as string | null,
    action: 'rewrite' as 'rewrite' | 'expand' | 'simplify',
    streamingText: '',
  });

  async function startSectionRewrite(sectionName: string, action: 'rewrite' | 'expand' | 'simplify', instruction?: string) {
    if (!authStore.token || !draftDocument.value) return;
    if (!(await ensureLatestDocumentSaved())) return;

    streamError.value = '';
    rewriteState.isRewriting = true;
    rewriteState.sectionName = sectionName;
    rewriteState.action = action;
    rewriteState.streamingText = '';

    try {
      const response = await startRewriteMutation.mutateAsync({
        document_version: draftDocument.value.version,
        section_name: sectionName,
        action,
        instruction: instruction ?? null,
      });

      await consumeSectionStream(response.stream_url, authStore.token, {
        onSectionDelta(payload) {
          if (payload.delta) {
            rewriteState.streamingText += payload.delta;
          }
        },
        onSectionDocument(payload) {
          onApplyServerDocument(payload);
          rewriteState.streamingText = '';
        },
        onDocumentDone() {
          rewriteState.isRewriting = false;
          rewriteState.sectionName = null;
          rewriteState.streamingText = '';
          onRefetch();
          toast.success('改写完成', '请确认更新后的内容。');
        },
        onError(eventPayload) {
          streamError.value = eventPayload.message;
          rewriteState.isRewriting = false;
          rewriteState.sectionName = null;
          rewriteState.streamingText = '';
        },
      });
    } catch {
      streamError.value = '改写失败，请稍后再试。';
      rewriteState.isRewriting = false;
      rewriteState.sectionName = null;
      rewriteState.streamingText = '';
    }
  }

  return {
    rewriteState,
    startSectionRewrite,
  };
}
