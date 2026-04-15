<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import StatePanel from '@/shared/components/StatePanel.vue';

const authStore = useAuthStore();
const homeTarget = computed(() => (authStore.isAuthenticated ? { name: 'tasks' } : { name: 'landing' }));
</script>

<template>
  <section class="not-found-page">
    <StatePanel
      icon="🧭"
      eyebrow="404"
      title="这个页面走丢了"
      description="可能是链接过期了，或者地址输错了。"
      tone="empty"
    >
      <template #actions>
        <RouterLink class="button primary" :to="homeTarget">返回备课台</RouterLink>
      </template>
    </StatePanel>
  </section>
</template>
