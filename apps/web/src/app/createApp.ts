import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query';
import { createPinia, type Pinia } from 'pinia';
import { createApp as createClientApp, createSSRApp, type App as VueApp } from 'vue';
import { createMemoryHistory } from 'vue-router';

import App from '@/App.vue';
import { createAppRouter } from '@/app/router';

interface CreateLessonPilotAppOptions {
  ssr?: boolean;
}

export interface LessonPilotAppContext {
  app: VueApp;
  pinia: Pinia;
  router: ReturnType<typeof createAppRouter>;
  queryClient: QueryClient;
}

export function createLessonPilotApp(options: CreateLessonPilotAppOptions = {}): LessonPilotAppContext {
  const app = options.ssr ? createSSRApp(App) : createClientApp(App);
  const pinia = createPinia();
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: 1,
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: 0,
      },
    },
  });
  const router = createAppRouter(pinia, options.ssr ? createMemoryHistory() : undefined);

  app.use(pinia);
  app.use(router);
  app.use(VueQueryPlugin, { queryClient });

  return { app, pinia, router, queryClient };
}
