<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useLogoutMutation } from '@/features/auth/composables/useAuth';

const router = useRouter();
const authStore = useAuthStore();
const logoutMutation = useLogoutMutation();

const open = ref(false);
const rootRef = ref<HTMLElement | null>(null);

const userName = computed(() => authStore.user?.name?.trim() || '老师');
const userInitial = computed(() => userName.value.slice(0, 1).toUpperCase());

function handleOutsideClick(event: MouseEvent) {
  if (!rootRef.value?.contains(event.target as Node)) {
    open.value = false;
  }
}

async function logout() {
  try {
    if (authStore.token) {
      await logoutMutation.mutateAsync();
    }
  } catch {
    // Ignore remote logout failures and clear the local session anyway.
  }

  authStore.clearSession();
  open.value = false;
  await router.push({ name: 'login' });
}

async function goToSettings() {
  open.value = false;
  await router.push({ name: 'settings' });
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick);
});
</script>

<template>
  <div ref="rootRef" class="user-menu">
    <button class="user-menu-trigger" type="button" @click="open = !open">
      <span class="user-menu-avatar">{{ userInitial }}</span>
      <span class="user-menu-name">{{ userName }}</span>
      <span class="user-menu-caret">▾</span>
    </button>

    <div v-if="open" class="user-menu-panel app-card">
      <div class="user-menu-label">当前账户</div>
      <div class="user-menu-panel-name">{{ userName }}</div>
      <button class="user-menu-item" type="button" @click="goToSettings">账户设置</button>
      <button class="user-menu-item danger" type="button" @click="logout">退出登录</button>
    </div>
  </div>
</template>
