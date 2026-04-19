<script setup lang="ts">
import { ref } from 'vue';

defineProps<{
  source: string;
  title: string;
  chapter?: string;
  snippet: string;
}>();

const show = ref(false);
</script>

<template>
  <sup
    class="cite-label"
    @mouseenter="show = true"
    @mouseleave="show = false"
  >
    <span class="cite-marker">[{{ source }}]</span>
    <Transition name="cite-fade">
      <div v-if="show" class="cite-tooltip">
        <div class="cite-tooltip-title">{{ title }}</div>
        <div v-if="chapter" class="cite-tooltip-chapter">{{ chapter }}</div>
        <div class="cite-tooltip-snippet">{{ snippet }}</div>
      </div>
    </Transition>
  </sup>
</template>

<style scoped>
.cite-label {
  position: relative;
  display: inline-flex;
  cursor: help;
}

.cite-marker {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: var(--radius-pill);
  background: var(--badge-bg);
  color: var(--badge-text);
  font-size: 12px;
  font-weight: 600;
  line-height: 1.2;
  border: 1px solid rgba(var(--primary-rgb), 0.1);
}

.cite-tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 0;
  z-index: var(--z-dropdown);
  min-width: 240px;
  max-width: 360px;
  padding: 10px 12px;
  background: color-mix(in srgb, var(--surface) 86%, var(--surface-strong) 14%);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-elevated);
  font-size: 12px;
  line-height: 1.5;
  color: var(--text);
  pointer-events: none;
}

.cite-tooltip-title {
  font-weight: 600;
  margin-bottom: 2px;
}

.cite-tooltip-chapter {
  color: var(--text-tertiary);
  font-size: 11px;
  margin-bottom: 4px;
}

.cite-tooltip-snippet {
  color: var(--muted);
  font-size: 11px;
  white-space: normal;
}

.cite-fade-enter-active,
.cite-fade-leave-active {
  transition: opacity 0.15s ease;
}

.cite-fade-enter-from,
.cite-fade-leave-to {
  opacity: 0;
}
</style>
