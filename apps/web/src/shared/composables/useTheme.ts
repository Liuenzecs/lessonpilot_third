import { computed, reactive } from 'vue';

import {
  savePersistedThemePreference,
  type PersistedThemePreference,
} from '@/shared/utils/storage';

export type AppTheme = PersistedThemePreference;

const themeState = reactive({
  value: 'light' as AppTheme,
  initialized: false,
});

function resolveInitialTheme(): AppTheme {
  // 主流程固定使用亮色主题；暗色主题仅保留给内部实验调用。
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
