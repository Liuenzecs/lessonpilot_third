<script setup lang="ts">
defineProps<{
  title: string;
  isCurrent: boolean;
}>();
</script>

<template>
  <div class="section-skeleton" :class="{ current: isCurrent }">
    <div class="section-skeleton-head">
      <div class="section-skeleton-title">{{ title }}</div>
      <div class="section-skeleton-badge">{{ isCurrent ? '正在生成' : '等待生成' }}</div>
    </div>
    <div class="section-skeleton-line short" />
    <div class="section-skeleton-line" />
    <div class="section-skeleton-line medium" />
  </div>
</template>
