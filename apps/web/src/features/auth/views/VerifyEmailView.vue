<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useVerifyEmailMutation } from '@/features/auth/composables/useAuth';

const authStore = useAuthStore();
const verifyEmailMutation = useVerifyEmailMutation();
const status = ref<'idle' | 'success' | 'error'>('idle');

const token = computed(() => {
  if (typeof window === 'undefined') {
    return '';
  }
  return new URLSearchParams(window.location.search).get('token') || '';
});

async function verify() {
  if (!token.value) {
    status.value = 'error';
    return;
  }

  try {
    const user = await verifyEmailMutation.mutateAsync({ token: token.value });
    if (authStore.user && authStore.user.id === user.id) {
      authStore.setUser(user);
    }
    status.value = 'success';
  } catch {
    status.value = 'error';
  }
}

onMounted(() => {
  void verify();
});
</script>

<template>
  <div class="auth-card app-card">
    <p class="muted">LessonPilot</p>
    <h1 class="auth-title">验证邮箱</h1>
    <p class="subtitle" v-if="status === 'idle'">正在验证你的邮箱，请稍候。</p>
    <p class="subtitle" v-else-if="status === 'success'">邮箱已验证成功，现在可以继续进入备课台。</p>
    <p class="subtitle" v-else>验证链接无效或已过期，请回到账户设置重新发送验证邮件。</p>

    <div class="auth-inline-stack">
      <RouterLink class="button primary" :to="{ name: authStore.isAuthenticated ? 'tasks' : 'login' }">
        {{ authStore.isAuthenticated ? '进入备课台' : '返回登录' }}
      </RouterLink>
    </div>
  </div>
</template>
