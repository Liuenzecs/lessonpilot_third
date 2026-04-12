import { ApiError, request } from '@/shared/api/client';
import { useAuthStore } from '@/app/stores/auth';
import type { AuthUser } from '@/features/auth/types';
import { createLessonPilotApp } from '@/app/createApp';
import { installAnalytics } from '@/features/analytics/client';
import { applySeo } from '@/app/seo';
import { initBrowserSentry } from '@/app/monitoring/sentry';
import '@/shared/styles/main.css';

async function bootstrap() {
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

  installAnalytics(router, pinia);
  router.afterEach((to) => {
    applySeo(to);
  });

  await router.isReady();
  applySeo(router.currentRoute.value);
  await initBrowserSentry(app, router);
  app.mount('#app', true);
}

void bootstrap();
