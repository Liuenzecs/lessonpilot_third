import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';

import type { DocumentListResponse, DocumentUpdatePayload, LessonDocument } from '@/features/editor/types';
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
