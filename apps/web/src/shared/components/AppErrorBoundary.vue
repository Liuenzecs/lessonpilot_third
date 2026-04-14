<script setup lang="ts">
import { onErrorCaptured, ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import StatePanel from '@/shared/components/StatePanel.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const error = ref<unknown>(null);

onErrorCaptured((capturedError) => {
  error.value = capturedError;
  console.error('Unhandled Vue error', capturedError);
  return false;
});

watch(
  () => route.fullPath,
  () => {
    error.value = null;
  },
);

function retry() {
  error.value = null;
}

function goToSafePage() {
  void router.push(authStore.isAuthenticated ? { name: 'tasks' } : { name: 'landing' });
}
</script>

<template>
  <slot v-if="!error" />
  <div v-else class="page-shell">
    <StatePanel
      icon="⚠"
      eyebrow="应用异常"
      title="页面刚刚遇到了一个未处理错误"
      description="你可以先重试当前页面，或者回到一个稳定入口继续使用 LessonPilot。"
      tone="error"
    >
      <template #actions>
        <button class="button primary" type="button" @click="retry">重试当前页面</button>
        <button class="button ghost" type="button" @click="goToSafePage">
          {{ authStore.isAuthenticated ? '返回备课台' : '回到首页' }}
        </button>
      </template>
    </StatePanel>
  </div>
</template>
