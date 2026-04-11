import { ApiError } from '@/shared/api/client';

function normalizeDetail(detail: unknown): string {
  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') {
          return item;
        }
        if (item && typeof item === 'object' && 'msg' in item) {
          return String(item.msg);
        }
        return '';
      })
      .filter(Boolean)
      .join('；');
  }

  return '';
}

export function getAuthErrorMessage(error: unknown, fallback: string): string {
  if (!(error instanceof ApiError)) {
    return fallback;
  }

  const detail =
    error.data && typeof error.data === 'object' && 'detail' in error.data
      ? normalizeDetail((error.data as { detail?: unknown }).detail)
      : '';

  if (error.status === 401) {
    return '登录失败，请检查邮箱和密码。';
  }

  if (error.status === 409) {
    return '该邮箱已经注册，请直接登录或更换邮箱。';
  }

  if (detail.includes('Password must be at least 8 characters')) {
    return '密码至少 8 位，并且必须同时包含字母和数字。';
  }

  if (detail) {
    return detail;
  }

  if (error.status >= 500) {
    return '服务暂时异常，请稍后重试。';
  }

  return fallback;
}
