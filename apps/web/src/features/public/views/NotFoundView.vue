<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';

const authStore = useAuthStore();
const homeTarget = computed(() => (authStore.isAuthenticated ? { name: 'tasks' } : { name: 'landing' }));
</script>

<template>
  <section class="not-found-page section-card">
    <div class="not-found-icon">📝 ?</div>
    <h1 class="page-title">这个页面走丢了</h1>
    <p class="subtitle">可能是链接过期了，或者地址输错了。</p>
    <RouterLink class="button primary" :to="homeTarget">回到备课台</RouterLink>
  </section>
</template>
