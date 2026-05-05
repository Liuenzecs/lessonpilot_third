import { useQuery } from '@tanstack/vue-query';

import { request } from '@/shared/api/client';

export interface UserUsage {
  generations_today: number;
  generations_this_month: number;
  daily_limit: number;
  monthly_limit: number;
  cost_this_month: number;
}

export function useUsage() {
  return useQuery<UserUsage>({
    queryKey: ['user-usage'],
    queryFn: () => request<UserUsage>('/api/v1/account/usage'),
    refetchInterval: 60_000,
  });
}
