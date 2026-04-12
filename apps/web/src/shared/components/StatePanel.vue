<script setup lang="ts">
withDefaults(
  defineProps<{
    icon?: string;
    eyebrow?: string;
    title: string;
    description: string;
    tone?: 'default' | 'info' | 'error' | 'empty';
    compact?: boolean;
  }>(),
  {
    icon: '·',
    eyebrow: '',
    tone: 'default',
    compact: false,
  },
);
</script>

<template>
  <section class="state-panel app-card" :class="[`tone-${tone}`, { compact }]">
    <div class="state-panel-icon">{{ icon }}</div>

    <div class="state-panel-copy">
      <p v-if="eyebrow" class="state-panel-eyebrow">{{ eyebrow }}</p>
      <h2 class="state-panel-title">{{ title }}</h2>
      <p class="state-panel-description">{{ description }}</p>
    </div>

    <div v-if="$slots.actions" class="button-row state-panel-actions">
      <slot name="actions" />
    </div>

    <div v-if="$slots.default" class="state-panel-extra">
      <slot />
    </div>
  </section>
</template>
