<script setup lang="ts">
defineProps<{
  text: string;
  active: boolean;
}>();
</script>

<template>
  <div class="streaming-section-card">
    <div class="streaming-text" :class="{ 'streaming-active': active }">
      {{ text }}<span v-if="active" class="streaming-cursor" />
    </div>
  </div>
</template>

<style scoped>
.streaming-section-card {
  padding: 16px 20px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-secondary);
}

.streaming-text {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.9375rem;
  line-height: 1.7;
  color: var(--text);
}

.streaming-cursor {
  display: inline-block;
  width: 2px;
  height: 1.1em;
  margin-left: 1px;
  vertical-align: text-bottom;
  background: var(--primary);
  animation: streaming-blink 0.8s step-end infinite;
}

@keyframes streaming-blink {
  50% { opacity: 0; }
}
</style>
