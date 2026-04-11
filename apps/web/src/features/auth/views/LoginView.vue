<script setup lang="ts">
import { computed, reactive } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useLoginMutation } from '@/features/auth/composables/useAuth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const loginMutation = useLoginMutation();
const form = reactive({
  email: '',
  password: '',
});

const infoMessage = computed(() => {
  if (route.query.reason === 'session_expired') {
    return '登录状态已失效，请重新登录后继续。';
  }
  return '';
});

const errorMessage = computed(() => {
  if (!loginMutation.error.value) {
    return '';
  }
  return '登录失败，请检查邮箱或密码。';
});

async function submit() {
  try {
    const response = await loginMutation.mutateAsync({ ...form });
    authStore.setSession(response.access_token, response.user);
    await router.push({ name: 'tasks' });
  } catch {
    // The mutation state already drives the inline error message.
  }
}
</script>

<template>
  <div class="auth-layout">
    <div class="auth-card app-card">
      <p class="muted">LessonPilot</p>
      <h1 class="auth-title">进入备课台</h1>
      <p class="subtitle">登录后继续你的结构化备课工作流。</p>

      <form @submit.prevent="submit">
        <label class="field">
          <span>邮箱</span>
          <input v-model.trim="form.email" type="email" autocomplete="email" required />
        </label>

        <label class="field">
          <span>密码</span>
          <input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            minlength="8"
            required
          />
        </label>

        <button class="button primary" type="submit" :disabled="loginMutation.isPending.value">
          {{ loginMutation.isPending.value ? '登录中...' : '登录' }}
        </button>
      </form>

      <div v-if="infoMessage" class="feedback">{{ infoMessage }}</div>
      <div v-if="errorMessage" class="feedback">{{ errorMessage }}</div>
      <p class="subtitle">
        还没有账号？
        <RouterLink to="/register" style="color: var(--primary)">注册</RouterLink>
      </p>
    </div>
  </div>
</template>
