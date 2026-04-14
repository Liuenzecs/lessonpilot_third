import { computed, reactive } from 'vue';

import {
  loadPersistedThemePreference,
  savePersistedThemePreference,
  type PersistedThemePreference,
} from '@/shared/utils/storage';

export type AppTheme = PersistedThemePreference;

const themeState = reactive({
  value: 'light' as AppTheme,
  initialized: false,
});

function resolveInitialTheme(): AppTheme {
  const persistedTheme = loadPersistedThemePreference();
  if (persistedTheme) {
    return persistedTheme;
  }
  if (typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

function applyTheme(theme: AppTheme, options: { persist?: boolean } = {}) {
  themeState.value = theme;
  if (typeof document !== 'undefined') {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
  }
  if (options.persist !== false) {
    savePersistedThemePreference(theme);
  }
}

export function initTheme() {
  if (!themeState.initialized) {
    themeState.initialized = true;
    applyTheme(resolveInitialTheme());
    return;
  }
  applyTheme(themeState.value, { persist: false });
}

export function useTheme() {
  return {
    theme: computed(() => themeState.value),
    isDark: computed(() => themeState.value === 'dark'),
    setTheme(theme: AppTheme) {
      applyTheme(theme);
    },
    toggleTheme() {
      applyTheme(themeState.value === 'dark' ? 'light' : 'dark');
    },
  };
}
