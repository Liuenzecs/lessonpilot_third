<script setup lang="ts">
import type { Block } from '@lessonpilot/shared-types';

import BlockPreview from '@/features/editor/components/BlockPreview.vue';

const props = withDefaults(
  defineProps<{
    block: Block;
    label?: string;
    canRegenerate?: boolean;
  }>(),
  {
    label: 'AI 待确认',
    canRegenerate: false,
  },
);

defineEmits<{
  accept: [];
  reject: [];
  regenerate: [];
}>();
</script>

<template>
  <div class="pending-card">
    <div class="pending-card-head">
      <div class="muted">{{ props.label }}</div>
      <div v-if="block.suggestion?.kind === 'replace'" class="pending-chip">替换建议</div>
    </div>
    <BlockPreview :block="block" />
    <div class="button-row">
      <button class="button primary" type="button" @click="$emit('accept')">接受</button>
      <button class="button ghost" type="button" @click="$emit('reject')">拒绝</button>
      <button
        v-if="props.canRegenerate"
        class="button secondary"
        type="button"
        @click="$emit('regenerate')"
      >
        重新生成
      </button>
    </div>
  </div>
</template>
