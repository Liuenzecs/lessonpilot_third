<script setup lang="ts">
const props = defineProps<{
  title: string;
  updatedAt: string;
  sections: Array<{ id: string; title: string; paragraphs: string[] }>;
}>();
</script>

<template>
  <section class="legal-page">
    <div class="legal-hero">
      <p class="page-eyebrow">{{ props.title }}</p>
      <h1 class="page-title">{{ props.title }}</h1>
      <p class="subtitle">最后更新：{{ props.updatedAt }}</p>
    </div>

    <div class="legal-layout">
      <aside class="legal-nav app-card">
        <a v-for="section in props.sections" :key="section.id" :href="`#${section.id}`">
          {{ section.title }}
        </a>
      </aside>

      <div class="legal-content">
        <article
          v-for="section in props.sections"
          :id="section.id"
          :key="section.id"
          class="legal-section app-card"
        >
          <h2>{{ section.title }}</h2>
          <p v-for="paragraph in section.paragraphs" :key="paragraph">{{ paragraph }}</p>
        </article>
      </div>
    </div>
  </section>
</template>
