<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useRegisterMutation } from '@/features/auth/composables/useAuth';
import { getAuthErrorMessage } from '@/features/auth/utils/error';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const registerMutation = useRegisterMutation();
const showPassword = ref(false);
const form = reactive({
  name: '',
  email: '',
  password: '',
});

const errorMessage = computed(() => {
  if (!registerMutation.error.value) {
    return '';
  }
  return getAuthErrorMessage(
    registerMutation.error.value,
    '注册失败，请确认邮箱未被使用且密码不少于 8 位。',
  );
});

async function submit() {
  try {
    const response = await registerMutation.mutateAsync({ ...form });
    authStore.setSession(response.access_token, response.user);
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
    // Inline error state is enough here.
  }
}
</script>

<template>
  <div class="auth-card app-card">
    <p class="muted">LessonPilot</p>
    <h1 class="auth-title">创建你的备课账号</h1>
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
        <span class="field-help">至少 8 位，包含字母和数字</span>
      </label>

      <button class="button primary auth-submit" type="submit" :disabled="registerMutation.isPending.value">
        {{ registerMutation.isPending.value ? '创建中...' : '创建账号' }}
      </button>
    </form>

    <p class="auth-terms">
      注册即表示你同意
      <RouterLink :to="{ name: 'terms' }" class="auth-link">服务条款</RouterLink>
      和
      <RouterLink :to="{ name: 'privacy' }" class="auth-link">隐私政策</RouterLink>
    </p>

    <div class="auth-divider">或</div>
    <button class="auth-wechat-button" type="button" disabled>微信登录（即将支持）</button>

    <div v-if="errorMessage" class="feedback">{{ errorMessage }}</div>
    <p class="subtitle">
      已有账号？
      <RouterLink :to="{ name: 'login', query: route.query }" class="auth-link">登录</RouterLink>
    </p>
  </div>
</template>
