import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';

import type { MessageResponse } from '@/features/auth/types';
import type {
  AccountChangePasswordPayload,
  AccountDeletePayload,
  AccountRead,
  AccountUpdatePayload,
  FeedbackCreatePayload,
  FeedbackRead,
} from '@/features/settings/types';
import { download, request } from '@/shared/api/client';

export function useAccount() {
  return useQuery({
    queryKey: ['account'],
    queryFn: () => request<AccountRead>('/api/v1/account'),
  });
}

export function useUpdateAccountMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: AccountUpdatePayload) =>
      request<AccountRead>('/api/v1/account', {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
    onSuccess: (account) => {
      queryClient.setQueryData(['account'], account);
    },
  });
}

export function useChangePasswordMutation() {
  return useMutation({
    mutationFn: (payload: AccountChangePasswordPayload) =>
      request<MessageResponse>('/api/v1/account/change-password', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  });
}

export function useExportAccountMutation() {
  return useMutation({
    mutationFn: async () => {
      const blob = await download('/api/v1/account/export', { method: 'POST' });
      return blob;
    },
  });
}

export function useDeleteAccountMutation() {
  return useMutation({
    mutationFn: (payload: AccountDeletePayload) =>
      request<void>('/api/v1/account', {
        method: 'DELETE',
        body: JSON.stringify(payload),
      }),
  });
}

export function useFeedbackMutation() {
  return useMutation({
    mutationFn: (payload: FeedbackCreatePayload) =>
      request<FeedbackRead>('/api/v1/account/feedback', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  });
}
