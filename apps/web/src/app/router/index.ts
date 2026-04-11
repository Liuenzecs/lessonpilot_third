import type { Pinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import LoginView from '@/features/auth/views/LoginView.vue';
import RegisterView from '@/features/auth/views/RegisterView.vue';
import EditorView from '@/features/editor/views/EditorView.vue';
import TaskCreateView from '@/features/task/views/TaskCreateView.vue';
import TaskListView from '@/features/task/views/TaskListView.vue';

export function createAppRouter(pinia: Pinia) {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      {
        path: '/',
        redirect: '/tasks',
      },
      {
        path: '/login',
        name: 'login',
        component: LoginView,
        meta: { guestOnly: true },
      },
      {
        path: '/register',
        name: 'register',
        component: RegisterView,
        meta: { guestOnly: true },
      },
      {
        path: '/tasks',
        name: 'tasks',
        component: TaskListView,
        meta: { requiresAuth: true },
      },
      {
        path: '/tasks/new',
        name: 'task-create',
        component: TaskCreateView,
        meta: { requiresAuth: true },
      },
      {
        path: '/tasks/:taskId/editor',
        name: 'editor',
        component: EditorView,
        meta: { requiresAuth: true },
      },
    ],
  });

  router.beforeEach((to) => {
    const authStore = useAuthStore(pinia);
    if (!authStore.hydrated) {
      authStore.hydrate();
    }

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      return { name: 'login' };
    }

    if (to.meta.guestOnly && authStore.isAuthenticated) {
      return { name: 'tasks' };
    }

    return true;
  });

  return router;
}
