<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useAdminAccess } from '@/app/adminAccess';
import { useLogoutMutation } from '@/features/auth/composables/useAuth';
import { useToast } from '@/shared/composables/useToast';

const router = useRouter();
const authStore = useAuthStore();
const { isAdmin } = useAdminAccess();
const logoutMutation = useLogoutMutation();
const toast = useToast();

const open = ref(false);
const rootRef = ref<HTMLElement | null>(null);

const userName = computed(() => authStore.user?.name?.trim() || '老师');
const userInitial = computed(() => userName.value.slice(0, 1).toUpperCase());

function handleOutsideClick(event: MouseEvent) {
  if (!rootRef.value?.contains(event.target as Node)) {
    open.value = false;
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
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
  toast.info('你已退出登录');
  await router.push({ name: 'login' });
}

async function goToSettings() {
  open.value = false;
  await router.push({ name: 'settings' });
}

async function goToAdmin() {
  open.value = false;
  await router.push({ name: 'admin-overview' });
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick);
  window.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick);
  window.removeEventListener('keydown', handleKeydown);
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
      <button v-if="isAdmin" class="user-menu-item" type="button" @click="goToAdmin">管理后台</button>
      <button class="user-menu-item" type="button" @click="goToSettings">账户设置</button>
      <button class="user-menu-item danger" type="button" @click="logout">退出登录</button>
    </div>
  </div>
</template>
