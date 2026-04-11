<script setup lang="ts">
import { changelogEntries } from '@/features/public/content';
</script>

<template>
  <section class="section-card changelog-page">
    <p class="page-eyebrow">更新日志</p>
    <h1 class="page-title">LessonPilot 的阶段进展</h1>
    <div class="changelog-list">
      <article v-for="entry in changelogEntries" :key="`${entry.date}-${entry.title}`" class="changelog-item app-card">
        <div class="changelog-date">{{ entry.date }}</div>
        <h2>{{ entry.title }}</h2>
        <ul class="feature-bullets">
          <li v-for="item in entry.items" :key="item">{{ item }}</li>
        </ul>
      </article>
    </div>
  </section>
</template>
