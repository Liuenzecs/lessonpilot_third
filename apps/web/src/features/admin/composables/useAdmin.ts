import { computed, type Ref } from 'vue';
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';

import { request } from '@/shared/api/client';
import { useAdminAccess } from '@/app/adminAccess';
import type {
  AdminOverviewRead,
  AdminUserDetailRead,
  AdminUserListResponse,
  QuotaAdjustmentCreatePayload,
  QuotaAdjustmentListResponse,
  QuotaAdjustmentRecord,
} from '@/features/admin/types';

export function useAdminOverview() {
  return useQuery({
    queryKey: ['admin', 'overview'],
    queryFn: () => request<AdminOverviewRead>('/api/v1/admin/overview'),
  });
}

export function useAdminUsers(filters: { query: Ref<string>; plan: Ref<string>; status: Ref<string> }) {
  const params = computed(() => {
    const search = new URLSearchParams();
    if (filters.query.value) {
      search.set('query', filters.query.value);
    }
    if (filters.plan.value) {
      search.set('plan', filters.plan.value);
    }
    if (filters.status.value) {
      search.set('status', filters.status.value);
    }
    return search.toString();
  });

  return useQuery({
    queryKey: computed(() => ['admin', 'users', filters.query.value, filters.plan.value, filters.status.value]),
    queryFn: () =>
      request<AdminUserListResponse>(`/api/v1/admin/users${params.value ? `?${params.value}` : ''}`),
  });
}

export function useAdminUserDetail(userId: string) {
  return useQuery({
    queryKey: ['admin', 'users', userId],
    queryFn: () => request<AdminUserDetailRead>(`/api/v1/admin/users/${userId}`),
    enabled: Boolean(userId),
  });
}

export function useQuotaAdjustments(userId: string) {
  return useQuery({
    queryKey: ['admin', 'users', userId, 'quota-adjustments'],
    queryFn: () => request<QuotaAdjustmentListResponse>(`/api/v1/admin/users/${userId}/quota-adjustments`),
    enabled: Boolean(userId),
  });
}

export function useCreateQuotaAdjustment(userId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: QuotaAdjustmentCreatePayload) =>
      request<QuotaAdjustmentRecord>(`/api/v1/admin/users/${userId}/quota-adjustments`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['admin', 'users', userId] });
      void queryClient.invalidateQueries({ queryKey: ['admin', 'users', userId, 'quota-adjustments'] });
    },
  });
}

export function useAdminGuard() {
  const access = useAdminAccess();
  return {
    isAdmin: access.isAdmin,
  };
}
