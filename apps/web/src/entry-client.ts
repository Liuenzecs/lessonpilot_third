import { ApiError, request } from '@/shared/api/client';
import { useAuthStore } from '@/app/stores/auth';
import type { AuthUser } from '@/features/auth/types';
import { createLessonPilotApp } from '@/app/createApp';
import { initTheme } from '@/shared/composables/useTheme';
import '@/shared/styles/main.css';

async function bootstrap() {
  initTheme();
  const { app, pinia, router } = createLessonPilotApp();

  const authStore = useAuthStore(pinia);
  authStore.hydrate();

  if (authStore.token) {
    try {
      const user = await request<AuthUser>('/api/v1/auth/me');
      authStore.setSession(authStore.token, user);
    } catch (error) {
      if (!(error instanceof ApiError && error.status === 401)) {
        console.error('Failed to restore session.', error);
      }
      authStore.clearSession();
    }
  }

  await router.isReady();
  app.mount('#app', true);
}

void bootstrap();
