<script setup lang="ts">
defineProps<{
  isGenerating: boolean;
  completed: number;
  total: number;
  currentSection: string;
  isRewriting: boolean;
  rewriteAction: 'rewrite' | 'polish' | 'expand';
  isAppending: boolean;
  appendSectionTitle: string;
  streamError: string;
  noticeText: string;
  noticeTone: 'success' | 'info';
}>();
</script>

<template>
  <div class="editor-status-stack">
    <div v-if="noticeText" class="generation-banner" :class="{ success: noticeTone === 'success' }">
      {{ noticeText }}
    </div>

    <div v-if="isGenerating" class="generation-banner">
      正在生成 {{ currentSection || '教案内容' }}
      <template v-if="total">（{{ completed }}/{{ total }}）</template>
    </div>

    <div v-if="isRewriting" class="generation-banner secondary">
      AI 正在{{ rewriteAction === 'rewrite' ? '重写' : rewriteAction === 'polish' ? '润色' : '扩写' }}当前内容
    </div>

    <div v-if="isAppending" class="generation-banner secondary">
      AI 正在为 {{ appendSectionTitle || '当前章节' }} 补充内容
    </div>

    <div v-if="streamError" class="feedback">{{ streamError }}</div>
  </div>
</template>
