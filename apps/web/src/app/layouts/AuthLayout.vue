<script setup lang="ts">
import { RouterView } from 'vue-router';

import PublicFooter from '@/features/public/components/PublicFooter.vue';
import PublicNav from '@/features/public/components/PublicNav.vue';

import '@/features/public/styles/public.css';
</script>

<template>
  <div class="auth-shell">
    <PublicNav />

    <main class="auth-shell-main">
      <RouterView />
    </main>

    <PublicFooter />
  </div>
</template>
