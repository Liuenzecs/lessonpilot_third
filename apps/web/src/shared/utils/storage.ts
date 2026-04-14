const AUTH_STORAGE_KEY = 'lessonpilot.auth';
export const THEME_STORAGE_KEY = 'lessonpilot-theme';

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

export type PersistedThemePreference = 'light' | 'dark';

export function loadPersistedThemePreference(): PersistedThemePreference | null {
  if (!canUseStorage()) {
    return null;
  }
  const rawValue = localStorage.getItem(THEME_STORAGE_KEY);
  return rawValue === 'light' || rawValue === 'dark' ? rawValue : null;
}

export function savePersistedThemePreference(theme: PersistedThemePreference): void {
  if (!canUseStorage()) {
    return;
  }
  localStorage.setItem(THEME_STORAGE_KEY, theme);
}
