<script setup lang="ts">
import { RouterLink } from 'vue-router';

import StatePanel from '@/shared/components/StatePanel.vue';
</script>

<template>
  <section class="not-found-page">
    <StatePanel
      icon="🛠"
      eyebrow="500"
      title="服务器暂时开了小差"
      description="你可以稍后重试，或者先回到备课台继续其他工作。"
      tone="error"
    >
      <template #actions>
        <RouterLink class="button primary" :to="{ name: 'tasks' }">返回备课台</RouterLink>
        <RouterLink class="button ghost" :to="{ name: 'help' }">去帮助中心</RouterLink>
      </template>
    </StatePanel>
  </section>
</template>
