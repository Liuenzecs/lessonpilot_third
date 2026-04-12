import type { AccountSubscriptionRead } from '@/features/settings/types';
import { ApiError } from '@/shared/api/client';

export interface BillingErrorDetail {
  code: 'quota_exceeded' | 'plan_required';
  message: string;
  subscription: AccountSubscriptionRead;
}

export function getBillingErrorDetail(error: unknown): BillingErrorDetail | null {
  if (!(error instanceof ApiError)) {
    return null;
  }

  const detail =
    error.data && typeof error.data === 'object' && 'detail' in error.data
      ? (error.data as { detail?: unknown }).detail
      : null;

  if (!detail || typeof detail !== 'object' || !('code' in detail) || !('message' in detail) || !('subscription' in detail)) {
    return null;
  }

  const code = (detail as { code?: string }).code;
  if (code !== 'quota_exceeded' && code !== 'plan_required') {
    return null;
  }

  return {
    code,
    message: String((detail as { message?: unknown }).message ?? ''),
    subscription: (detail as { subscription: AccountSubscriptionRead }).subscription,
  };
}

export function formatBillingDate(value: string | null): string {
  if (!value) {
    return '未设置';
  }
  return new Date(value).toLocaleString();
}

export function formatCountdown(value: string | null): string {
  if (!value) {
    return '';
  }
  const diff = new Date(value).getTime() - Date.now();
  if (diff <= 0) {
    return '已到期';
  }
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
  return `剩余 ${days} 天`;
}

export function formatAmount(amountCents: number): string {
  return `¥${(amountCents / 100).toFixed(2)}`;
}
