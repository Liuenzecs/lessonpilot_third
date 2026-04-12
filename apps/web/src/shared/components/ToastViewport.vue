<script setup lang="ts">
import { useToast } from '@/shared/composables/useToast';

const toast = useToast();
</script>

<template>
  <div class="toast-viewport" aria-live="polite" aria-atomic="true">
    <TransitionGroup name="toast-list" tag="div" class="toast-stack">
      <article
        v-for="item in toast.toasts.value"
        :key="item.id"
        class="toast-card app-card"
        :class="`level-${item.level}`"
      >
        <div class="toast-card-copy">
          <div class="toast-card-title">{{ item.title }}</div>
          <div v-if="item.description" class="toast-card-description">{{ item.description }}</div>
        </div>

        <div class="toast-card-actions">
          <button
            v-if="item.action"
            class="button ghost toast-card-button"
            type="button"
            @click="item.action.onClick?.()"
          >
            {{ item.action.label }}
          </button>

          <button
            v-if="item.dismissible !== false"
            class="toast-close"
            type="button"
            aria-label="关闭提示"
            @click="toast.remove(item.id)"
          >
            ×
          </button>
        </div>
      </article>
    </TransitionGroup>
  </div>
</template>
