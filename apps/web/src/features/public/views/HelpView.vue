<script setup lang="ts">
import { computed, ref } from 'vue';

import FaqAccordion from '@/features/public/components/FaqAccordion.vue';
import { helpGroups } from '@/features/public/content';

const search = ref('');

const filteredGroups = computed(() => {
  const keyword = search.value.trim().toLowerCase();
  if (!keyword) {
    return helpGroups;
  }

  return helpGroups
    .map((group) => ({
      ...group,
      items: group.items.filter((item) =>
        [item.question, item.answer].some((value) => value.toLowerCase().includes(keyword)),
      ),
    }))
    .filter((group) => group.items.length > 0);
});
</script>

<template>
  <div class="help-page">
    <section class="section-card">
      <p class="page-eyebrow">帮助中心</p>
      <h1 class="page-title">搜索你的问题</h1>
      <p class="subtitle">用大白话解释功能、AI 行为、账户和数据相关问题。</p>

      <label class="help-search app-card">
        <span>🔍</span>
        <input v-model.trim="search" type="text" placeholder="搜索你的问题..." />
      </label>
    </section>

    <section
      v-for="group in filteredGroups"
      :key="group.title"
      class="help-group section-card"
    >
      <div class="landing-section-head">
        <p class="page-eyebrow">{{ group.title }}</p>
        <h2>{{ group.title }}</h2>
      </div>
      <FaqAccordion :items="group.items" />
    </section>
  </div>
</template>
