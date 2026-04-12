import { clearPersistedAuthState } from '@/shared/utils/storage';

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export function getApiBaseUrl(): string {
  return (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
}

export function buildApiUrl(path: string): string {
  return `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
}

function handleUnauthorized(path: string): void {
  const isAuthFormSubmit =
    path.startsWith('/api/v1/auth/login') || path.startsWith('/api/v1/auth/register');
  if (isAuthFormSubmit) {
    return;
  }

  clearPersistedAuthState();
  if (typeof window === 'undefined') {
    return;
  }

  if (window.location.pathname !== '/login') {
    window.location.replace('/login?reason=session_expired');
  }
}

function getToken(): string | null {
  if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
    return null;
  }
  const rawValue = localStorage.getItem('lessonpilot.auth');
  if (!rawValue) {
    return null;
  }

  try {
    return (JSON.parse(rawValue) as { token?: string | null }).token ?? null;
  } catch {
    return null;
  }
}

async function parseErrorBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    return await response.json();
  }
  const text = await response.text();
  return text ? { detail: text } : { detail: '' };
}

export async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (!(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(buildApiUrl(path), {
      ...init,
      headers,
    });
  } catch (error) {
    throw new ApiError('Network request failed', 0, {
      detail: error instanceof Error ? error.message : 'Network request failed',
    });
  }

  if (!response.ok) {
    if (response.status === 401) {
      handleUnauthorized(path);
    }
    const errorBody = await parseErrorBody(response);
    throw new ApiError(`Request failed with status ${response.status}`, response.status, errorBody);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function download(path: string, init: RequestInit = {}): Promise<Blob> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!(init.body instanceof FormData) && init.body) {
    headers.set('Content-Type', 'application/json');
  }

  let response: Response;
  try {
    response = await fetch(buildApiUrl(path), { ...init, headers });
  } catch (error) {
    throw new ApiError('Network request failed', 0, {
      detail: error instanceof Error ? error.message : 'Network request failed',
    });
  }

  if (!response.ok) {
    if (response.status === 401) {
      handleUnauthorized(path);
    }
    const errorBody = await parseErrorBody(response);
    throw new ApiError(`Download failed with status ${response.status}`, response.status, errorBody);
  }
  return await response.blob();
}
