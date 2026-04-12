<script setup lang="ts">
withDefaults(
  defineProps<{
    eyebrow?: string;
    title: string;
    description: string;
    stepLabel?: string;
  }>(),
  {
    eyebrow: '新手引导',
    stepLabel: '',
  },
);
</script>

<template>
  <aside class="onboarding-callout app-card">
    <div class="onboarding-callout-head">
      <div class="onboarding-callout-copy">
        <div class="onboarding-callout-eyebrow-row">
          <span class="onboarding-callout-eyebrow">{{ eyebrow }}</span>
          <span v-if="stepLabel" class="onboarding-callout-step">{{ stepLabel }}</span>
        </div>
        <h3 class="onboarding-callout-title">{{ title }}</h3>
        <p class="onboarding-callout-description">{{ description }}</p>
      </div>
    </div>

    <div v-if="$slots.actions" class="button-row onboarding-callout-actions">
      <slot name="actions" />
    </div>
  </aside>
</template>

<style scoped>
.onboarding-callout {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 22px;
  border-color: rgba(88, 107, 182, 0.2);
  background: linear-gradient(180deg, rgba(246, 248, 255, 0.98), rgba(255, 255, 255, 0.96));
  box-shadow: 0 18px 32px rgba(37, 55, 83, 0.08);
}

.onboarding-callout-copy {
  display: grid;
  gap: 8px;
}

.onboarding-callout-eyebrow-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.onboarding-callout-eyebrow,
.onboarding-callout-step {
  width: fit-content;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.onboarding-callout-eyebrow {
  background: rgba(62, 98, 143, 0.1);
  color: var(--primary);
}

.onboarding-callout-step {
  background: rgba(112, 126, 208, 0.12);
  color: #5866b5;
}

.onboarding-callout-title {
  margin: 0;
  font-size: 20px;
}

.onboarding-callout-description {
  margin: 0;
  color: var(--muted);
}

.onboarding-callout-actions {
  flex-wrap: wrap;
}
</style>
