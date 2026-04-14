<script setup lang="ts">
defineProps<{
  isGenerating: boolean;
  completed: number;
  total: number;
  currentSection: string;
  isRewriting: boolean;
  rewriteAction: 'rewrite' | 'expand' | 'simplify';
  isAppending: boolean;
  appendSectionTitle: string;
  streamError: string;
  noticeText: string;
  noticeTone: 'success' | 'info';
}>();

defineEmits<{
  stop: [];
}>();

function getRewriteLabel(action: 'rewrite' | 'expand' | 'simplify') {
  if (action === 'expand') return '扩写';
  if (action === 'simplify') return '精简';
  return '重写';
}
</script>

<template>
  <div class="editor-status-stack">
    <div v-if="noticeText" class="generation-banner" :class="{ success: noticeTone === 'success' }">
      {{ noticeText }}
    </div>

    <div v-if="isGenerating" class="generation-banner generating">
      <span>
        正在生成 {{ currentSection || '教案内容' }}
        <template v-if="total">（{{ completed }}/{{ total }}）</template>
      </span>
      <button class="button ghost stop-btn" type="button" @click="$emit('stop')">停止生成</button>
    </div>

    <div v-if="isRewriting" class="generation-banner secondary">
      AI 正在{{ getRewriteLabel(rewriteAction) }}当前内容
    </div>

    <div v-if="streamError" class="feedback">{{ streamError }}</div>
  </div>
</template>

<style scoped>
.stop-btn {
  margin-left: 12px;
  padding: 2px 10px;
  font-size: 0.8125rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-secondary);
}

.stop-btn:hover {
  color: var(--danger, #c75450);
  border-color: var(--danger, #c75450);
}
</style>
