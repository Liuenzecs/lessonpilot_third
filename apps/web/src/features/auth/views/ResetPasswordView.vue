<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';

import { useResetPasswordMutation } from '@/features/auth/composables/useAuth';

const route = useRoute();
const router = useRouter();
const resetPasswordMutation = useResetPasswordMutation();

const token = computed(() => String(route.query.token || ''));
const form = reactive({
  password: '',
  confirm_password: '',
});
const showPassword = ref(false);
const successMessage = ref('');

const errorMessage = computed(() => {
  if (!token.value) {
    return '重置链接无效，请重新发起密码重置。';
  }
  if (!resetPasswordMutation.error.value) {
    return '';
  }
  return '重置密码失败，请确认链接仍然有效。';
});

async function submit() {
  await resetPasswordMutation.mutateAsync({
    token: token.value,
    password: form.password,
    confirm_password: form.confirm_password,
  });
  successMessage.value = '密码已重置，正在带你回到登录页。';
  window.setTimeout(() => {
    void router.push({ name: 'login', query: { reset: 'success' } });
  }, 800);
}
</script>

<template>
  <div class="auth-card app-card">
    <p class="muted">LessonPilot</p>
    <h1 class="auth-title">设置新密码</h1>
    <p class="subtitle">新密码至少 8 位，并同时包含字母和数字。</p>

    <form @submit.prevent="submit">
      <label class="field">
        <span>新密码</span>
        <div class="password-field">
          <input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="new-password"
            minlength="8"
            required
          />
          <button class="password-toggle" type="button" @click="showPassword = !showPassword">
            {{ showPassword ? '隐藏' : '显示' }}
          </button>
        </div>
      </label>

      <label class="field">
        <span>确认新密码</span>
        <input
          v-model="form.confirm_password"
          :type="showPassword ? 'text' : 'password'"
          autocomplete="new-password"
          minlength="8"
          required
        />
      </label>

      <button class="button primary auth-submit" type="submit" :disabled="resetPasswordMutation.isPending.value || !token">
        {{ resetPasswordMutation.isPending.value ? '提交中...' : '确认重置' }}
      </button>
    </form>

    <p v-if="successMessage" class="feedback success">{{ successMessage }}</p>
    <p v-else-if="errorMessage" class="feedback">{{ errorMessage }}</p>
    <p class="subtitle">
      <RouterLink :to="{ name: 'login' }" class="auth-link">返回登录</RouterLink>
    </p>
  </div>
</template>
