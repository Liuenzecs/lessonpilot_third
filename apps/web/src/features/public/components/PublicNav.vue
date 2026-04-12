<script setup lang="ts">
import { getActivePinia } from 'pinia';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { trackClientEvent } from '@/features/analytics/client';
import UserMenu from '@/shared/components/UserMenu.vue';

const authStore = useAuthStore();
const route = useRoute();
const menuOpen = ref(false);
const isScrolled = ref(false);
const pinia = getActivePinia();

const isLoginRoute = computed(() => route.name === 'login');
const isRegisterRoute = computed(() => route.name === 'register');
const isAuthRoute = computed(() => isLoginRoute.value || isRegisterRoute.value);
const guestActionLabel = computed(() => (isLoginRoute.value ? '注册' : '登录'));
const guestActionTarget = computed(() => (isLoginRoute.value ? { name: 'register' } : { name: 'login' }));

function trackNavCta(ctaId: string, location: string) {
  if (!pinia) {
    return;
  }
  trackClientEvent(pinia, 'cta_click', route.path, { cta_id: ctaId, location });
}

function handleScroll() {
  isScrolled.value = window.scrollY > 10;
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    menuOpen.value = false;
  }
}

watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false;
  },
);

onMounted(() => {
  handleScroll();
  window.addEventListener('scroll', handleScroll, { passive: true });
  window.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll);
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
  <header class="public-nav" :class="{ scrolled: isScrolled }">
    <div class="public-nav-inner">
      <RouterLink class="public-brand" :to="{ name: 'landing' }">LessonPilot</RouterLink>

      <button class="public-nav-mobile" type="button" @click="menuOpen = !menuOpen">☰</button>

      <nav class="public-nav-links" :class="{ open: menuOpen }">
        <template v-if="!authStore.isAuthenticated">
          <RouterLink :to="{ name: 'landing', hash: '#features' }">功能介绍</RouterLink>
          <RouterLink :to="{ name: 'pricing' }">定价</RouterLink>
          <RouterLink :to="{ name: 'help' }">帮助中心</RouterLink>

          <template v-if="isAuthRoute">
            <RouterLink class="public-nav-login" :to="guestActionTarget" @click="trackNavCta('auth_switch', 'public_nav')">
              {{ guestActionLabel }}
            </RouterLink>
          </template>

          <template v-else>
            <RouterLink class="public-nav-login" :to="{ name: 'login' }" @click="trackNavCta('login', 'public_nav')">
              登录
            </RouterLink>
            <RouterLink class="button primary public-nav-cta" :to="{ name: 'register' }" @click="trackNavCta('start', 'public_nav')">
              开始使用
            </RouterLink>
          </template>
        </template>

        <template v-else>
          <RouterLink :to="{ name: 'help' }">帮助中心</RouterLink>
          <RouterLink :to="{ name: 'tasks' }">备课台</RouterLink>
          <UserMenu />
        </template>
      </nav>
    </div>
  </header>
</template>
