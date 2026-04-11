import { useMutation } from '@tanstack/vue-query';

import type { AuthResponse, LoginPayload, RegisterPayload } from '@/features/auth/types';
import { request } from '@/shared/api/client';

export function useLoginMutation() {
  return useMutation({
    mutationFn: (payload: LoginPayload) =>
      request<AuthResponse>('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  });
}

export function useRegisterMutation() {
  return useMutation({
    mutationFn: (payload: RegisterPayload) =>
      request<AuthResponse>('/api/v1/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  });
}

export function useLogoutMutation() {
  return useMutation({
    mutationFn: () =>
      request<void>('/api/v1/auth/logout', {
        method: 'POST',
      }),
  });
}

