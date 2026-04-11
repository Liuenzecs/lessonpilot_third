<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  items: Array<{ question: string; answer: string }>;
}>();

const openIndex = ref<number | null>(null);

function toggle(index: number) {
  openIndex.value = openIndex.value === index ? null : index;
}
</script>

<template>
  <div class="faq-accordion">
    <article v-for="(item, index) in props.items" :key="item.question" class="faq-item app-card">
      <button class="faq-question" type="button" @click="toggle(index)">
        <span>{{ item.question }}</span>
        <span>{{ openIndex === index ? '−' : '+' }}</span>
      </button>
      <p v-if="openIndex === index" class="faq-answer">{{ item.answer }}</p>
    </article>
  </div>
</template>
