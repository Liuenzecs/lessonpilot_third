<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useVerifyEmailMutation } from '@/features/auth/composables/useAuth';
import { getAuthErrorMessage } from '@/features/auth/utils/error';
import { useToast } from '@/shared/composables/useToast';

const route = useRoute();
const authStore = useAuthStore();
const verifyEmailMutation = useVerifyEmailMutation();
const toast = useToast();
const status = ref<'idle' | 'success' | 'error'>('idle');

const token = computed(() => (route.query.token as string) || '');

async function verify() {
  if (!token.value) {
    status.value = 'error';
    toast.error('验证链接无效', '请回到账户设置重新发送验证邮件。');
    return;
  }

  try {
    const user = await verifyEmailMutation.mutateAsync({ token: token.value });
    if (authStore.user && authStore.user.id === user.id) {
      authStore.setUser(user);
    }
    status.value = 'success';
    toast.success('邮箱验证成功', '现在可以继续进入备课台。');
  } catch (error) {
    status.value = 'error';
    toast.error('邮箱验证失败', getAuthErrorMessage(error, '验证链接无效或已过期。'));
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
    <p class="subtitle" v-if="status === 'idle'">正在验证你的邮箱...</p>
    <p class="subtitle" v-else-if="status === 'success'">邮箱已验证成功，现在可以继续进入备课台。</p>
    <p class="subtitle" v-else>验证链接无效或已过期，请回到账户设置重新发送验证邮件。</p>

    <div class="auth-inline-stack">
      <RouterLink class="button primary" :to="{ name: authStore.isAuthenticated ? 'tasks' : 'login' }">
        {{ authStore.isAuthenticated ? '进入备课台' : '返回登录' }}
      </RouterLink>
    </div>
  </div>
</template>
