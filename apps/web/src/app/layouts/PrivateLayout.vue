<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router';

import UserMenu from '@/shared/components/UserMenu.vue';

import '@/features/public/styles/public.css';

const route = useRoute();
const isTasksRoute = computed(() => route.name === 'tasks');
</script>

<template>
  <div class="private-shell">
    <header class="private-nav app-card">
      <RouterLink class="public-brand" :to="{ name: 'tasks' }">LessonPilot</RouterLink>

      <nav class="private-nav-links">
        <RouterLink :to="{ name: 'help' }">帮助中心</RouterLink>
        <RouterLink :class="{ active: isTasksRoute }" :to="{ name: 'tasks' }">备课台</RouterLink>
      </nav>

      <UserMenu />
    </header>

    <main class="private-main">
      <RouterView />
    </main>
  </div>
</template>
