<script setup lang="ts">
import { RouterView } from 'vue-router';

import AppErrorBoundary from '@/shared/components/AppErrorBoundary.vue';
import ToastViewport from '@/shared/components/ToastViewport.vue';
</script>

<template>
  <AppErrorBoundary>
    <RouterView v-slot="{ Component, route: currentRoute }">
      <Transition name="page-shell-transition" mode="out-in">
        <component :is="Component" :key="currentRoute.fullPath" />
      </Transition>
    </RouterView>
  </AppErrorBoundary>
  <ToastViewport />
</template>
