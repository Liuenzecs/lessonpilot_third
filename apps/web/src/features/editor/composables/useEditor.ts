import type { ComputedRef, Ref } from 'vue';

import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';

import type {
  DocumentHistoryResponse,
  DocumentRewritePayload,
  DocumentRewriteStartResponse,
  DocumentListResponse,
  DocumentSnapshotRecord,
  DocumentUpdatePayload,
  LessonDocument,
  QualityCheckResponse,
  TeachingPackageRecord,
} from '@/features/editor/types';
import { request } from '@/shared/api/client';

export function useTaskDocuments(taskId: string) {
  return useQuery({
    queryKey: ['documents', taskId],
    queryFn: () => request<DocumentListResponse>(`/api/v1/documents/?task_id=${taskId}`),
    enabled: Boolean(taskId),
  });
}

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ['document', documentId],
    queryFn: () => request<LessonDocument>(`/api/v1/documents/${documentId}`),
    enabled: Boolean(documentId),
  });
}

export function useUpdateDocumentMutation(
  getDocumentId: () => string,
  getTaskId: () => string,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: DocumentUpdatePayload) =>
      request<LessonDocument>(`/api/v1/documents/${getDocumentId()}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
    onSuccess: (document) => {
      queryClient.setQueryData(['document', getDocumentId()], document);
      void queryClient.invalidateQueries({ queryKey: ['documents', getTaskId()] });
    },
  });
}

export function useStartDocumentRewriteMutation(getDocumentId: () => string) {
  return useMutation({
    mutationFn: (payload: DocumentRewritePayload) =>
      request<DocumentRewriteStartResponse>(`/api/v1/documents/${getDocumentId()}/rewrite`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  });
}

export function useDocumentHistory(
  documentId: Ref<string> | ComputedRef<string>,
  enabled: Ref<boolean> | ComputedRef<boolean>,
) {
  return useQuery({
    queryKey: ['document-history', documentId],
    queryFn: () =>
      request<DocumentHistoryResponse>(`/api/v1/documents/${documentId.value}/history?limit=10`),
    enabled,
  });
}

export function useDocumentSnapshot(
  documentId: Ref<string> | ComputedRef<string>,
  snapshotId: Ref<string> | ComputedRef<string>,
  enabled: Ref<boolean> | ComputedRef<boolean>,
) {
  return useQuery({
    queryKey: ['document-history', documentId, snapshotId],
    queryFn: () =>
      request<DocumentSnapshotRecord>(
        `/api/v1/documents/${documentId.value}/history/${snapshotId.value}`,
      ),
    enabled,
  });
}

export function useRestoreSnapshotMutation(
  getDocumentId: () => string,
  getTaskId: () => string,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (snapshotId: string) =>
      request<LessonDocument>(`/api/v1/documents/${getDocumentId()}/history/${snapshotId}/restore`, {
        method: 'POST',
      }),
    onSuccess: (document) => {
      queryClient.setQueryData(['document', getDocumentId()], document);
      void queryClient.invalidateQueries({ queryKey: ['documents', getTaskId()] });
      void queryClient.invalidateQueries({ queryKey: ['document-history', getDocumentId()] });
    },
  });
}

export function useQualityCheckMutation(getDocumentId: () => string) {
  return useMutation({
    mutationFn: () =>
      request<QualityCheckResponse>(`/api/v1/documents/${getDocumentId()}/quality-check`, {
        method: 'POST',
      }),
  });
}

export function useTeachingPackageMutation(getDocumentId: () => string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      request<TeachingPackageRecord>(`/api/v1/documents/${getDocumentId()}/teaching-package`, {
        method: 'POST',
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['teaching-packages', getDocumentId()] });
    },
  });
}
