import { useMutation } from '@tanstack/vue-query';

import type {
  AuthResponse,
  ForgotPasswordPayload,
  LoginPayload,
  MessageResponse,
  RegisterPayload,
  ResetPasswordPayload,
  VerifyEmailPayload,
} from '@/features/auth/types';
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

export function useForgotPasswordMutation() {
  return useMutation({
    mutationFn: (payload: ForgotPasswordPayload) =>
      request<MessageResponse>('/api/v1/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  });
}

export function useResetPasswordMutation() {
  return useMutation({
    mutationFn: (payload: ResetPasswordPayload) =>
      request<MessageResponse>('/api/v1/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  });
}

export function useResendVerificationMutation() {
  return useMutation({
    mutationFn: () =>
      request<MessageResponse>('/api/v1/auth/resend-verification', {
        method: 'POST',
      }),
  });
}

export function useVerifyEmailMutation() {
  return useMutation({
    mutationFn: (payload: VerifyEmailPayload) =>
      request<AuthResponse['user']>('/api/v1/auth/verify-email', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  });
}
