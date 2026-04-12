const AUTH_STORAGE_KEY = 'lessonpilot.auth';

export interface PersistedAuthState {
  token: string | null;
  user: unknown | null;
}

function canUseStorage(): boolean {
  return typeof window !== 'undefined' && typeof localStorage !== 'undefined';
}

export function loadPersistedAuthState(): PersistedAuthState {
  if (!canUseStorage()) {
    return { token: null, user: null };
  }
  const rawValue = localStorage.getItem(AUTH_STORAGE_KEY);
  if (!rawValue) {
    return { token: null, user: null };
  }

  try {
    return JSON.parse(rawValue) as PersistedAuthState;
  } catch {
    return { token: null, user: null };
  }
}

export function savePersistedAuthState(state: PersistedAuthState): void {
  if (!canUseStorage()) {
    return;
  }
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(state));
}

export function clearPersistedAuthState(): void {
  if (!canUseStorage()) {
    return;
  }
  localStorage.removeItem(AUTH_STORAGE_KEY);
}
