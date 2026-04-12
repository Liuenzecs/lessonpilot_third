import type { Pinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';

import AuthLayout from '@/app/layouts/AuthLayout.vue';
import PrivateLayout from '@/app/layouts/PrivateLayout.vue';
import PublicLayout from '@/app/layouts/PublicLayout.vue';
import { useAuthStore } from '@/app/stores/auth';
import ForgotPasswordView from '@/features/auth/views/ForgotPasswordView.vue';
import LoginView from '@/features/auth/views/LoginView.vue';
import RegisterView from '@/features/auth/views/RegisterView.vue';
import ResetPasswordView from '@/features/auth/views/ResetPasswordView.vue';
import VerifyEmailView from '@/features/auth/views/VerifyEmailView.vue';
import EditorView from '@/features/editor/views/EditorView.vue';
import AboutView from '@/features/public/views/AboutView.vue';
import ChangelogView from '@/features/public/views/ChangelogView.vue';
import HelpView from '@/features/public/views/HelpView.vue';
import LandingView from '@/features/public/views/LandingView.vue';
import NetworkErrorView from '@/features/public/views/NetworkErrorView.vue';
import NotFoundView from '@/features/public/views/NotFoundView.vue';
import PricingView from '@/features/public/views/PricingView.vue';
import PrivacyView from '@/features/public/views/PrivacyView.vue';
import ServerErrorView from '@/features/public/views/ServerErrorView.vue';
import TermsView from '@/features/public/views/TermsView.vue';
import SettingsView from '@/features/settings/views/SettingsView.vue';
import TaskCreateView from '@/features/task/views/TaskCreateView.vue';
import TaskListView from '@/features/task/views/TaskListView.vue';

export function createAppRouter(pinia: Pinia) {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      {
        path: '/',
        component: PublicLayout,
        children: [
          {
            path: '',
            name: 'landing',
            component: LandingView,
          },
          {
            path: 'pricing',
            name: 'pricing',
            component: PricingView,
          },
          {
            path: 'help',
            name: 'help',
            component: HelpView,
          },
          {
            path: 'about',
            name: 'about',
            component: AboutView,
          },
          {
            path: 'privacy',
            name: 'privacy',
            component: PrivacyView,
          },
          {
            path: 'terms',
            name: 'terms',
            component: TermsView,
          },
          {
            path: 'changelog',
            name: 'changelog',
            component: ChangelogView,
          },
          {
            path: '500',
            name: 'server-error',
            component: ServerErrorView,
          },
          {
            path: 'network-error',
            name: 'network-error',
            component: NetworkErrorView,
          },
          {
            path: ':pathMatch(.*)*',
            name: 'not-found',
            component: NotFoundView,
          },
        ],
      },
      {
        path: '/',
        component: AuthLayout,
        children: [
          {
            path: 'login',
            name: 'login',
            component: LoginView,
            meta: { guestOnly: true },
          },
          {
            path: 'register',
            name: 'register',
            component: RegisterView,
            meta: { guestOnly: true },
          },
          {
            path: 'forgot-password',
            name: 'forgot-password',
            component: ForgotPasswordView,
          },
          {
            path: 'reset-password',
            name: 'reset-password',
            component: ResetPasswordView,
          },
          {
            path: 'verify-email',
            name: 'verify-email',
            component: VerifyEmailView,
          },
        ],
      },
      {
        path: '/',
        component: PrivateLayout,
        meta: { requiresAuth: true },
        children: [
          {
            path: 'tasks',
            name: 'tasks',
            component: TaskListView,
          },
          {
            path: 'settings',
            name: 'settings',
            component: SettingsView,
          },
        ],
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
