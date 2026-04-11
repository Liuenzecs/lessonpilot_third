import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query';
import { createPinia } from 'pinia';
import { createApp } from 'vue';

import App from './App.vue';
import { createAppRouter } from './app/router';
import { useAuthStore } from './app/stores/auth';
import type { AuthUser } from './features/auth/types';
import { ApiError, request } from './shared/api/client';
import './shared/styles/main.css';

const app = createApp(App);
const pinia = createPinia();
const queryClient = new QueryClient();
const router = createAppRouter(pinia);

async function bootstrap() {
  app.use(pinia);
  const authStore = useAuthStore(pinia);
  authStore.hydrate();

  if (authStore.token) {
    try {
      const user = await request<AuthUser>('/api/v1/auth/me');
      authStore.setSession(authStore.token, user);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        authStore.clearSession();
      } else {
        console.error('Failed to restore session.', error);
      }
    }
  }

  app.use(router);
  app.use(VueQueryPlugin, { queryClient });
  app.mount('#app');
}

void bootstrap();
