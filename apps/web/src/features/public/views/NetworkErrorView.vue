<script setup lang="ts">
import { RouterLink } from 'vue-router';

import StatePanel from '@/shared/components/StatePanel.vue';
</script>

<template>
  <section class="not-found-page">
    <StatePanel
      icon="📡"
      eyebrow="网络错误"
      title="网络连接暂时不可用"
      description="请检查网络后重试；如果只是临时波动，也可以稍后再回来继续备课。"
      tone="error"
    >
      <template #actions>
        <RouterLink class="button primary" :to="{ name: 'tasks' }">返回备课台</RouterLink>
        <RouterLink class="button ghost" :to="{ name: 'help' }">去帮助中心</RouterLink>
      </template>
    </StatePanel>
  </section>
</template>
