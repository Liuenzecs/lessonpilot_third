/**
 * 自动保存 composable。
 * 从 useEditorView 中提取的自动保存逻辑：debounce、冲突处理、重试。
 */
import type { Ref } from 'vue';
import { onBeforeUnmount, watch } from 'vue';

import type { LessonDocument } from '@/features/editor/types';
import { useUpdateDocumentMutation } from '@/features/editor/composables/useEditor';
import { ApiError } from '@/shared/api/client';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';
import { cloneSerializable } from '@/shared/utils/content';

interface UseAutoSaveOptions {
  draftDocument: Ref<LessonDocument | null>;
  saveState: Ref<'saved' | 'dirty' | 'saving' | 'retrying' | 'error' | 'conflict'>;
  streamError: Ref<string>;
  suppressAutosave: Ref<boolean>;
  taskId: string;
  onApplyServerDocument: (doc: LessonDocument) => void;
}

export function useAutoSave(options: UseAutoSaveOptions) {
  const {
    draftDocument,
    saveState,
    streamError,
    suppressAutosave,
    taskId,
    onApplyServerDocument,
  } = options;

  const toast = useToast();
  let saveTimer: number | undefined;
  let retryTimer: number | undefined;
  let autosaveFailureAnnounced = false;
  let persistPromise: Promise<boolean> | null = null;

  const updateDocumentMutation = useUpdateDocumentMutation(
    () => draftDocument.value?.id ?? '',
    () => taskId,
  );

  function clearRetryTimer() {
    if (retryTimer) {
      window.clearTimeout(retryTimer);
      retryTimer = undefined;
    }
  }

  function scheduleAutosaveRetry(delay = 2000) {
    if (typeof window === 'undefined') return;
    clearRetryTimer();
    if (typeof navigator !== 'undefined' && navigator.onLine === false) return;
    retryTimer = window.setTimeout(() => {
      retryTimer = undefined;
      void persistDocument({ attempt: 'retry' });
    }, delay);
  }

  function handlePersistError(error: unknown, attempt: 'manual' | 'autosave' | 'retry'): false {
    if (error instanceof ApiError && error.status === 409) {
      clearRetryTimer();
      saveState.value = 'conflict';
      streamError.value = '检测到版本冲突，请先刷新最新版本，再决定是否重试保存。';
      autosaveFailureAnnounced = false;
      return false;
    }

    saveState.value = 'error';
    if (attempt === 'manual') {
      streamError.value = '保存失败，改动暂未同步。';
      toast.error('保存失败', getErrorDescription(error, '请稍后重试。'));
      return false;
    }

    streamError.value = '自动保存失败，改动暂未同步。';
    scheduleAutosaveRetry();
    if (!autosaveFailureAnnounced) {
      toast.error('自动保存失败', '改动暂未同步，网络恢复后会自动重试。');
      autosaveFailureAnnounced = true;
    }
    return false;
  }

  function applySave(doc: LessonDocument) {
    suppressAutosave.value = true;
    draftDocument.value = cloneSerializable(doc);
    saveState.value = 'saved';
    clearRetryTimer();
    streamError.value = '';
    onApplyServerDocument(doc);
    setTimeout(() => { suppressAutosave.value = false; }, 0);
  }

  async function persistDocument(options: { attempt?: 'manual' | 'autosave' | 'retry' } = {}): Promise<boolean> {
    if (!draftDocument.value) return false;
    if (persistPromise) return persistPromise;

    const attempt = options.attempt ?? 'manual';
    if (saveTimer) {
      window.clearTimeout(saveTimer);
      saveTimer = undefined;
    }
    clearRetryTimer();

    persistPromise = (async () => {
      saveState.value = attempt === 'retry' ? 'retrying' : 'saving';
      try {
        const updatedDocument = await updateDocumentMutation.mutateAsync({
          version: draftDocument.value!.version,
          content: draftDocument.value!.content,
        });
        applySave(updatedDocument);
        if (attempt === 'retry' || autosaveFailureAnnounced) {
          toast.success('自动保存已恢复');
        }
        autosaveFailureAnnounced = false;
        return true;
      } catch (error) {
        return handlePersistError(error, attempt);
      } finally {
        persistPromise = null;
      }
    })();

    return persistPromise;
  }

  async function ensureLatestDocumentSaved(): Promise<boolean> {
    if (!draftDocument.value) return false;

    if (saveTimer) {
      window.clearTimeout(saveTimer);
      saveTimer = undefined;
    }

    if (persistPromise) {
      const saved = await persistPromise;
      if (!saved) {
        streamError.value = saveState.value === 'conflict'
          ? '请先刷新最新版本，再继续当前操作。'
          : '请先处理未同步的改动，再继续当前操作。';
        return false;
      }
    }

    if (['dirty', 'saving', 'error', 'retrying'].includes(saveState.value)) {
      const saved = await persistDocument({ attempt: 'manual' });
      if (!saved) {
        streamError.value = saveState.value === 'conflict'
          ? '请先处理保存冲突，再继续当前操作。'
          : '请先处理未同步的改动，再继续当前操作。';
        return false;
      }
    }

    if (saveState.value === 'conflict') {
      streamError.value = '请先刷新最新版本，再继续当前操作。';
      return false;
    }

    return true;
  }

  function handleOnline() {
    if (!draftDocument.value) return;
    if (['error', 'retrying', 'dirty'].includes(saveState.value)) {
      clearRetryTimer();
      void persistDocument({ attempt: 'retry' });
    }
  }

  function handleOffline() {
    if (['dirty', 'saving', 'retrying'].includes(saveState.value)) {
      saveState.value = 'error';
      streamError.value = '网络连接已断开，改动暂未同步。';
      scheduleAutosaveRetry();
      if (!autosaveFailureAnnounced) {
        toast.error('网络已断开', '改动暂未同步，恢复网络后会自动重试。');
        autosaveFailureAnnounced = true;
      }
    }
  }

  // Auto-save watcher (700ms debounce)
  watch(
    () => draftDocument.value?.content,
    () => {
      if (!draftDocument.value || suppressAutosave.value) return;
      saveState.value = 'dirty';
      streamError.value = '';
      if (saveTimer) window.clearTimeout(saveTimer);
      saveTimer = window.setTimeout(() => {
        saveTimer = undefined;
        void persistDocument({ attempt: 'autosave' });
      }, 700);
    },
    { deep: true },
  );

  onBeforeUnmount(() => {
    if (saveTimer) window.clearTimeout(saveTimer);
    clearRetryTimer();
  });

  return {
    persistDocument,
    ensureLatestDocumentSaved,
    handleOnline,
    handleOffline,
  };
}
