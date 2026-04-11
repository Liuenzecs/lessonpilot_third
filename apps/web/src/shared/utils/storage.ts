const AUTH_STORAGE_KEY = 'lessonpilot.auth';

export interface PersistedAuthState {
  token: string | null;
  user: unknown | null;
}

export function loadPersistedAuthState(): PersistedAuthState {
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
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(state));
}

export function clearPersistedAuthState(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

