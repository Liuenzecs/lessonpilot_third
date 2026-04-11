<script setup lang="ts">
import { RouterView } from 'vue-router';

import PublicFooter from '@/features/public/components/PublicFooter.vue';
import PublicNav from '@/features/public/components/PublicNav.vue';

import '@/features/public/styles/public.css';
</script>

<template>
  <div class="public-shell">
    <PublicNav />
    <main class="public-main">
      <RouterView />
    </main>
    <PublicFooter />
  </div>
</template>
