<script setup lang="ts">
import { computed, reactive } from 'vue';
import { RouterLink, useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useRegisterMutation } from '@/features/auth/composables/useAuth';

const router = useRouter();
const authStore = useAuthStore();
const registerMutation = useRegisterMutation();
const form = reactive({
  name: '',
  email: '',
  password: '',
});

const errorMessage = computed(() => {
  if (!registerMutation.error.value) {
    return '';
  }
  return '注册失败，请确认邮箱未被使用且密码不少于 8 位。';
});

async function submit() {
  try {
    const response = await registerMutation.mutateAsync({ ...form });
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
      <h1 class="auth-title">创建备课账号</h1>
      <p class="subtitle">几分钟内拿到结构化教案草稿，后续只管微调。</p>

      <form @submit.prevent="submit">
        <label class="field">
          <span>姓名</span>
          <input v-model.trim="form.name" type="text" minlength="2" required />
        </label>

        <label class="field">
          <span>邮箱</span>
          <input v-model.trim="form.email" type="email" autocomplete="email" required />
        </label>

        <label class="field">
          <span>密码</span>
          <input
            v-model="form.password"
            type="password"
            autocomplete="new-password"
            minlength="8"
            required
          />
        </label>

        <button class="button primary" type="submit" :disabled="registerMutation.isPending.value">
          {{ registerMutation.isPending.value ? '创建中...' : '创建账号' }}
        </button>
      </form>

      <div v-if="errorMessage" class="feedback">{{ errorMessage }}</div>
      <p class="subtitle">
        已有账号？
        <RouterLink to="/login" style="color: var(--primary)">登录</RouterLink>
      </p>
    </div>
  </div>
</template>
