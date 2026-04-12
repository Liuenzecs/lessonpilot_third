import type { RouterHistory } from 'vue-router';
import { createRouter, createWebHistory } from 'vue-router';
import type { Pinia } from 'pinia';

import AuthLayout from '@/app/layouts/AuthLayout.vue';
import PrivateLayout from '@/app/layouts/PrivateLayout.vue';
import PublicLayout from '@/app/layouts/PublicLayout.vue';
import AdminLayout from '@/app/layouts/AdminLayout.vue';
import { useAuthStore } from '@/app/stores/auth';

const LandingView = () => import('@/features/public/views/LandingView.vue');
const PricingView = () => import('@/features/public/views/PricingView.vue');
const HelpView = () => import('@/features/public/views/HelpView.vue');
const AboutView = () => import('@/features/public/views/AboutView.vue');
const PrivacyView = () => import('@/features/public/views/PrivacyView.vue');
const TermsView = () => import('@/features/public/views/TermsView.vue');
const ChangelogView = () => import('@/features/public/views/ChangelogView.vue');
const ServerErrorView = () => import('@/features/public/views/ServerErrorView.vue');
const NetworkErrorView = () => import('@/features/public/views/NetworkErrorView.vue');
const NotFoundView = () => import('@/features/public/views/NotFoundView.vue');

const LoginView = () => import('@/features/auth/views/LoginView.vue');
const RegisterView = () => import('@/features/auth/views/RegisterView.vue');
const ForgotPasswordView = () => import('@/features/auth/views/ForgotPasswordView.vue');
const ResetPasswordView = () => import('@/features/auth/views/ResetPasswordView.vue');
const VerifyEmailView = () => import('@/features/auth/views/VerifyEmailView.vue');

const TaskListView = () => import('@/features/task/views/TaskListView.vue');
const TaskCreateView = () => import('@/features/task/views/TaskCreateView.vue');
const SettingsView = () => import('@/features/settings/views/SettingsView.vue');
const EditorView = () => import('@/features/editor/views/EditorView.vue');

const AdminOverviewView = () => import('@/features/admin/views/AdminOverviewView.vue');
const AdminUsersView = () => import('@/features/admin/views/AdminUsersView.vue');
const AdminUserDetailView = () => import('@/features/admin/views/AdminUserDetailView.vue');

export function createAppRouter(pinia: Pinia, history: RouterHistory = createWebHistory()) {
  const router = createRouter({
    history,
    routes: [
      {
        path: '/',
        component: PublicLayout,
        children: [
          {
            path: '',
            name: 'landing',
            component: LandingView,
            meta: { publicSsr: true, seoKey: 'landing' },
          },
          {
            path: 'pricing',
            name: 'pricing',
            component: PricingView,
            meta: { publicSsr: true, seoKey: 'pricing' },
          },
          {
            path: 'help',
            name: 'help',
            component: HelpView,
            meta: { publicSsr: true, seoKey: 'help' },
          },
          {
            path: 'about',
            name: 'about',
            component: AboutView,
            meta: { publicSsr: true, seoKey: 'about' },
          },
          {
            path: 'privacy',
            name: 'privacy',
            component: PrivacyView,
            meta: { publicSsr: true, seoKey: 'privacy' },
          },
          {
            path: 'terms',
            name: 'terms',
            component: TermsView,
            meta: { publicSsr: true, seoKey: 'terms' },
          },
          {
            path: 'changelog',
            name: 'changelog',
            component: ChangelogView,
            meta: { publicSsr: true, seoKey: 'changelog' },
          },
          {
            path: '500',
            name: 'server-error',
            component: ServerErrorView,
            meta: { seoKey: 'notFound' },
          },
          {
            path: 'network-error',
            name: 'network-error',
            component: NetworkErrorView,
            meta: { seoKey: 'notFound' },
          },
          {
            path: ':pathMatch(.*)*',
            name: 'not-found',
            component: NotFoundView,
            meta: { publicSsr: true, seoKey: 'notFound' },
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
      {
        path: '/admin',
        component: AdminLayout,
        meta: { requiresAuth: true },
        children: [
          {
            path: '',
            name: 'admin-overview',
            component: AdminOverviewView,
            meta: { hideFeedback: true },
          },
          {
            path: 'users',
            name: 'admin-users',
            component: AdminUsersView,
            meta: { hideFeedback: true },
          },
          {
            path: 'users/:userId',
            name: 'admin-user-detail',
            component: AdminUserDetailView,
            meta: { hideFeedback: true },
          },
        ],
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
