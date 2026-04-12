import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';

import type { MessageResponse } from '@/features/auth/types';
import type {
  AccountChangePasswordPayload,
  AccountDeletePayload,
  AccountRead,
  AccountSubscriptionRead,
  AccountUpdatePayload,
  BillingOrderListResponse,
  FeedbackCreatePayload,
  FeedbackRead,
  InvoiceRequestCreatePayload,
  InvoiceRequestListResponse,
  SubscriptionActionResponse,
  SubscriptionCheckoutPayload,
} from '@/features/settings/types';
import { download, request } from '@/shared/api/client';

export function useAccount() {
  return useQuery({
    queryKey: ['account'],
    queryFn: () => request<AccountRead>('/api/v1/account'),
  });
}

export function useSubscription() {
  return useQuery({
    queryKey: ['account', 'subscription'],
    queryFn: () => request<AccountSubscriptionRead>('/api/v1/account/subscription'),
  });
}

export function useSubscriptionOrders() {
  return useQuery({
    queryKey: ['account', 'subscription', 'orders'],
    queryFn: () => request<BillingOrderListResponse>('/api/v1/account/subscription/orders'),
  });
}

export function useInvoiceRequests() {
  return useQuery({
    queryKey: ['account', 'invoice-requests'],
    queryFn: () => request<InvoiceRequestListResponse>('/api/v1/account/invoice-requests'),
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

function invalidateBillingQueries(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: ['account', 'subscription'] });
  void queryClient.invalidateQueries({ queryKey: ['account', 'subscription', 'orders'] });
  void queryClient.invalidateQueries({ queryKey: ['account', 'invoice-requests'] });
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

export function useStartTrialMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      request<SubscriptionActionResponse>('/api/v1/account/subscription/trial', {
        method: 'POST',
      }),
    onSuccess: () => {
      invalidateBillingQueries(queryClient);
    },
  });
}

export function useCheckoutMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SubscriptionCheckoutPayload) =>
      request<SubscriptionActionResponse>('/api/v1/account/subscription/checkout', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      invalidateBillingQueries(queryClient);
    },
  });
}

export function useRenewSubscriptionMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SubscriptionCheckoutPayload) =>
      request<SubscriptionActionResponse>('/api/v1/account/subscription/renew', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      invalidateBillingQueries(queryClient);
    },
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

export function useCreateInvoiceRequestMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: InvoiceRequestCreatePayload) =>
      request('/api/v1/account/invoice-requests', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      invalidateBillingQueries(queryClient);
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
