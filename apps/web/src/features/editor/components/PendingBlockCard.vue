<script setup lang="ts">
import type { Block } from '@lessonpilot/shared-types';

import BlockRenderer from '@/features/editor/components/BlockRenderer.vue';

defineProps<{
  block: Block;
}>();

defineEmits<{
  accept: [];
  reject: [];
}>();
</script>

<template>
  <div class="pending-card">
    <div class="muted">AI 待确认</div>
    <BlockRenderer :block="block" readonly />
    <div class="button-row">
      <button class="button primary" type="button" @click="$emit('accept')">接受</button>
      <button class="button ghost" type="button" @click="$emit('reject')">拒绝</button>
    </div>
  </div>
</template>

