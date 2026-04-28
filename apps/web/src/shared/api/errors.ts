import { ApiError } from '@/shared/api/client';

export type AppErrorKind =
  | 'network'
  | 'not_found'
  | 'unauthorized'
  | 'rate_limited'
  | 'conflict'
  | 'server'
  | 'unknown';

export interface AppErrorState {
  kind: AppErrorKind;
  status: number | null;
  title: string;
  description: string;
}

function normalizeDetail(detail: unknown): string {
  if (typeof detail === 'string') {
    return detail.trim();
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') {
          return item;
        }
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg?: unknown }).msg ?? '').trim();
        }
        return '';
      })
      .filter(Boolean)
      .join('；');
  }

  if (detail && typeof detail === 'object') {
    if ('message' in detail && typeof (detail as { message?: unknown }).message === 'string') {
      return String((detail as { message: string }).message).trim();
    }
    if ('detail' in detail) {
      return normalizeDetail((detail as { detail?: unknown }).detail);
    }
  }

  return '';
}

export function extractApiErrorDetail(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return '';
  }

  return normalizeDetail(error.data);
}

export function getAppErrorState(
  error: unknown,
  defaults?: {
    defaultTitle?: string;
    defaultDescription?: string;
  },
): AppErrorState {
  const defaultTitle = defaults?.defaultTitle ?? '出了点问题';
  const defaultDescription = defaults?.defaultDescription ?? '请稍后重试。';

  if (!(error instanceof ApiError)) {
    return {
      kind: 'unknown',
      status: null,
      title: defaultTitle,
      description: defaultDescription,
    };
  }

  const detail = extractApiErrorDetail(error);

  if (error.status === 0) {
    return {
      kind: 'network',
      status: 0,
      title: '网络连接暂时不可用',
      description: detail || '请检查网络连接后重试，或稍后再回来继续备课。',
    };
  }

  if (error.status === 401) {
    return {
      kind: 'unauthorized',
      status: 401,
      title: '登录状态已失效',
      description: detail || '请重新登录后继续当前操作。',
    };
  }

  if (error.status === 429) {
    return {
      kind: 'rate_limited',
      status: 429,
      title: '请求过于频繁',
      description: detail || '请稍后再试，避免过快重复提交相同操作。',
    };
  }

  if (error.status === 402) {
    return {
      kind: 'unknown',
      status: 402,
      title: '当前能力暂不可用',
      description: detail || defaultDescription,
    };
  }

  if (error.status === 404) {
    return {
      kind: 'not_found',
      status: 404,
      title: '你要找的内容不存在了',
      description: detail || '它可能已被删除、移动，或链接已经失效。',
    };
  }

  if (error.status === 409) {
    return {
      kind: 'conflict',
      status: 409,
      title: '内容版本发生了变化',
      description: detail || '请刷新最新内容后再继续操作，避免覆盖别人的修改。',
    };
  }

  if (error.status >= 500) {
    return {
      kind: 'server',
      status: error.status,
      title: '服务器暂时开了小差',
      description: detail || '服务正在恢复中，请稍后重试。',
    };
  }

  return {
    kind: 'unknown',
    status: error.status,
    title: defaultTitle,
    description: detail || defaultDescription,
  };
}

export function getErrorDescription(error: unknown, fallback = '请稍后重试。'): string {
  const state = getAppErrorState(error, {
    defaultDescription: fallback,
  });
  return state.description || fallback;
}
