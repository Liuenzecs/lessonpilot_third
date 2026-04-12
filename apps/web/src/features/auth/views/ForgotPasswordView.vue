<script setup lang="ts">
import { onBeforeUnmount, reactive, ref } from 'vue';
import { RouterLink } from 'vue-router';

import { useForgotPasswordMutation } from '@/features/auth/composables/useAuth';
import { getAuthErrorMessage } from '@/features/auth/utils/error';
import { useToast } from '@/shared/composables/useToast';

const forgotPasswordMutation = useForgotPasswordMutation();
const toast = useToast();
const form = reactive({ email: '' });
const sentTo = ref('');
const cooldown = ref(0);
let timerId: number | null = null;

function startCooldown() {
  cooldown.value = 60;
  if (timerId) {
    window.clearInterval(timerId);
  }
  timerId = window.setInterval(() => {
    cooldown.value -= 1;
    if (cooldown.value <= 0 && timerId) {
      window.clearInterval(timerId);
      timerId = null;
    }
  }, 1000);
}

onBeforeUnmount(() => {
  if (timerId) {
    window.clearInterval(timerId);
    timerId = null;
  }
});

async function submit() {
  const email = form.email.trim();
  try {
    await forgotPasswordMutation.mutateAsync({ email });
    sentTo.value = email;
    startCooldown();
    toast.success('重置链接已发送', `请检查邮箱 ${email}。`);
  } catch (error) {
    toast.error('发送重置链接失败', getAuthErrorMessage(error, '请稍后重试。'));
  }
}
</script>

<template>
  <div class="auth-card app-card">
    <p class="muted">LessonPilot</p>
    <h1 class="auth-title">{{ sentTo ? '重置链接已发送' : '重置密码' }}</h1>
    <p class="subtitle" v-if="!sentTo">输入你的注册邮箱，我们会发送重置链接。</p>
    <p class="subtitle" v-else>请检查邮箱 {{ sentTo }}，没收到可以在倒计时结束后重新发送。</p>

    <form v-if="!sentTo" @submit.prevent="submit">
      <label class="field">
        <span>邮箱</span>
        <input v-model.trim="form.email" type="email" autocomplete="email" required />
      </label>

      <button class="button primary auth-submit" type="submit" :disabled="forgotPasswordMutation.isPending.value">
        {{ forgotPasswordMutation.isPending.value ? '发送中...' : '发送重置链接' }}
      </button>
    </form>

    <div v-else class="auth-inline-stack">
      <button class="button ghost" type="button" :disabled="cooldown > 0" @click="submit">
        {{ cooldown > 0 ? `重新发送（${cooldown}s）` : '重新发送' }}
      </button>
    </div>
    <p class="subtitle">
      想起来了？
      <RouterLink :to="{ name: 'login' }" class="auth-link">返回登录</RouterLink>
    </p>
  </div>
</template>
