import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';
import type { Ref } from 'vue';

import type {
  ShareCommentCreate,
  ShareCommentRead,
  ShareLinkCreate,
  ShareLinkRead,
  ShareLinkUpdate,
  SharedDocumentView,
} from '@/features/sharing/types';
import { request } from '@/shared/api/client';

// ---------------------------------------------------------------------------
// Owner queries / mutations
// ---------------------------------------------------------------------------

export function useShareLinks(documentId: Ref<string | null>, enabled: Ref<boolean>) {
  return useQuery({
    queryKey: ['share-links', documentId],
    queryFn: () => request<ShareLinkRead[]>(`/api/v1/documents/${documentId.value}/shares`),
    enabled,
  });
}

export function useCreateShareLinkMutation(documentId: Ref<string>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ShareLinkCreate) =>
      request<ShareLinkRead>(`/api/v1/documents/${documentId.value}/share`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['share-links', documentId.value] });
    },
  });
}

export function useUpdateShareLinkMutation(documentId: Ref<string>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ shareId, payload }: { shareId: string; payload: ShareLinkUpdate }) =>
      request<ShareLinkRead>(`/api/v1/shares/${shareId}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['share-links', documentId.value] });
    },
  });
}

export function useDeleteShareLinkMutation(documentId: Ref<string>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (shareId: string) =>
      request<void>(`/api/v1/shares/${shareId}`, { method: 'DELETE' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['share-links', documentId.value] });
    },
  });
}

// ---------------------------------------------------------------------------
// Public reader queries / mutations
// ---------------------------------------------------------------------------

export function useSharedDocument(token: Ref<string>, enabled: Ref<boolean>) {
  return useQuery({
    queryKey: ['shared-document', token],
    queryFn: () => request<SharedDocumentView>(`/api/v1/share/${token.value}`),
    enabled,
  });
}

export function useSharedComments(token: Ref<string>, enabled: Ref<boolean>) {
  return useQuery({
    queryKey: ['shared-comments', token],
    queryFn: () => request<ShareCommentRead[]>(`/api/v1/share/${token.value}/comments`),
    enabled,
  });
}

export function usePostCommentMutation(token: Ref<string>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ShareCommentCreate) =>
      request<ShareCommentRead>(`/api/v1/share/${token.value}/comments`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['shared-comments', token.value] });
    },
  });
}
