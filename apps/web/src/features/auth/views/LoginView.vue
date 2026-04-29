<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useLoginMutation } from '@/features/auth/composables/useAuth';
import { getAuthErrorMessage } from '@/features/auth/utils/error';
import { useToast } from '@/shared/composables/useToast';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const loginMutation = useLoginMutation();
const toast = useToast();
const showPassword = ref(false);
const form = reactive({
  email: '',
  password: '',
});

const infoMessage = computed(() => {
  if (route.query.reason === 'session_expired') {
    return '登录状态已失效，请重新登录后继续。';
  }
  if (route.query.reset === 'success') {
    return '密码已重置，请使用新密码登录。';
  }
  return '';
});

const errorMessage = computed(() => {
  if (!loginMutation.error.value) {
    return '';
  }
  return getAuthErrorMessage(loginMutation.error.value, '登录失败，请检查邮箱或密码。');
});

async function submit() {
  try {
    const response = await loginMutation.mutateAsync({ ...form });
    authStore.setSession(response.access_token, response.user);
    toast.success('登录成功', '欢迎回到备课台。');
    if (route.query.upgrade === '1') {
      await router.push({
        name: 'tasks',
        query: {
          upgrade: '1',
          cycle: route.query.cycle === 'monthly' ? 'monthly' : 'yearly',
        },
      });
      return;
    }
    await router.push({ name: 'tasks' });
  } catch {
    // Inline error state remains the source of truth for credential issues.
  }
}
</script>

<template>
  <div class="auth-card app-card">
    <p class="muted">LessonPilot</p>
    <h1 class="auth-title">欢迎回来</h1>
    <p class="subtitle">登录后继续进入备课台。</p>

    <form @submit.prevent="submit">
      <label class="field">
        <span>邮箱</span>
        <input v-model.trim="form.email" type="email" autocomplete="email" required />
      </label>

      <label class="field">
        <span>密码</span>
        <div class="password-field">
          <input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            minlength="8"
            required
          />
          <button class="password-toggle" type="button" @click="showPassword = !showPassword">
            {{ showPassword ? '隐藏' : '显示' }}
          </button>
        </div>
      </label>

      <div class="auth-inline-row">
        <span />
        <RouterLink class="auth-link subtle" :to="{ name: 'forgot-password' }">忘记密码？</RouterLink>
      </div>

      <button class="button primary auth-submit" type="submit" :disabled="loginMutation.isPending.value">
        {{ loginMutation.isPending.value ? '登录中...' : '登录' }}
      </button>
    </form>

    <div class="auth-divider">或</div>
    <button class="auth-wechat-button" type="button" disabled>更多登录方式即将推出</button>

    <div v-if="infoMessage" class="feedback success">{{ infoMessage }}</div>
    <div v-if="errorMessage" class="feedback">{{ errorMessage }}</div>
    <p class="subtitle">
      没有账号？
      <RouterLink :to="{ name: 'register', query: route.query }" class="auth-link">免费注册</RouterLink>
    </p>
  </div>
</template>
