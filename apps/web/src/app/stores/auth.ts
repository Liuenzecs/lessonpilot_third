import { defineStore, type Pinia } from 'pinia';

import type { AuthUser } from '@/features/auth/types';
import {
  clearPersistedAuthState,
  loadPersistedAuthState,
  savePersistedAuthState,
} from '@/shared/utils/storage';

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  hydrated: boolean;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: null,
    user: null,
    hydrated: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token && state.user),
  },
  actions: {
    hydrate() {
      const persistedState = loadPersistedAuthState();
      this.token = persistedState.token;
      this.user = (persistedState.user as AuthUser | null) ?? null;
      this.hydrated = true;
    },
    setSession(token: string, user: AuthUser) {
      this.token = token;
      this.user = user;
      this.hydrated = true;
      savePersistedAuthState({ token, user });
    },
    setUser(user: AuthUser) {
      this.user = user;
      this.hydrated = true;
      savePersistedAuthState({ token: this.token, user });
    },
    clearSession() {
      this.token = null;
      this.user = null;
      this.hydrated = true;
      clearPersistedAuthState();
    },
  },
});

export function useAuthStoreWithPinia(pinia: Pinia) {
  return useAuthStore(pinia);
}
