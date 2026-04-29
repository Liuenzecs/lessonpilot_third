<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router';
import { BookOpen, Calendar, Settings } from 'lucide-vue-next';

import UserMenu from '@/shared/components/UserMenu.vue';

import '@/features/public/styles/public.css';

const route = useRoute();
const isTasksRoute = computed(() => route.name === 'tasks');
const isCalendarRoute = computed(() => route.name === 'calendar');
const isSettingsRoute = computed(() => route.name === 'settings');
</script>

<template>
  <div class="private-shell">
    <header class="private-nav">
      <RouterLink class="public-brand" :to="{ name: 'landing' }">LessonPilot</RouterLink>

      <nav class="private-nav-links">
        <RouterLink :to="{ name: 'help' }">帮助中心</RouterLink>
        <RouterLink :class="{ active: isTasksRoute }" :to="{ name: 'tasks' }">备课台</RouterLink>
      </nav>

      <UserMenu />
    </header>

    <main class="private-main">
      <RouterView />
    </main>

    <!-- Mobile bottom tab bar -->
    <nav class="private-mobile-tabs">
      <RouterLink :class="{ active: isTasksRoute }" :to="{ name: 'tasks' }" class="mobile-tab">
        <BookOpen :size="20" />
        <span>备课</span>
      </RouterLink>
      <RouterLink :class="{ active: isCalendarRoute }" :to="{ name: 'calendar' }" class="mobile-tab">
        <Calendar :size="20" />
        <span>日历</span>
      </RouterLink>
      <RouterLink :class="{ active: isSettingsRoute }" :to="{ name: 'settings' }" class="mobile-tab">
        <Settings :size="20" />
        <span>设置</span>
      </RouterLink>
    </nav>
  </div>
</template>

<style>
.private-mobile-tabs {
  display: none;
}

@media (max-width: 719px) {
  .private-mobile-tabs {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 30;
    justify-content: space-around;
    align-items: center;
    padding: 6px 4px;
    background: var(--surface);
    border-top: 1px solid var(--border);
    box-shadow: 0 -1px 4px rgba(0,0,0,0.06);
  }

  .mobile-tab {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 5px 10px;
    border-radius: var(--radius-micro);
    color: var(--muted);
    text-decoration: none;
    font-size: 11px;
    font-weight: 700;
  }

  .mobile-tab.active {
    color: var(--primary);
    background: rgba(var(--primary-rgb), 0.08);
  }

  .private-main {
    padding-bottom: 64px;
  }
}
</style>
