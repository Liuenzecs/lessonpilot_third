<script setup lang="ts">
import { computed } from 'vue';

import { containsFormula, parseFormulaSegments } from '@/shared/utils/formula';

const props = withDefaults(
  defineProps<{
    text: string;
    preview?: boolean;
  }>(),
  {
    preview: false,
  },
);

const hasFormula = computed(() => containsFormula(props.text));
const segments = computed(() => parseFormulaSegments(props.text));
</script>

<template>
  <span
    v-if="hasFormula"
    class="formula-text"
    :class="{ 'formula-text-preview': preview }"
  >
    <template v-for="(segment, index) in segments" :key="index">
      <span v-if="segment.kind === 'text'" class="formula-copy">{{ segment.content }}</span>
      <span
        v-else
        class="formula-math"
        :class="{ 'formula-math-display': segment.displayMode }"
        v-html="segment.html"
      />
    </template>
  </span>
</template>
