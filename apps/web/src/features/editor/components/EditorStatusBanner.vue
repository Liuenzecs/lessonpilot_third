<script setup lang="ts">
import { computed } from 'vue';

import type { AssetStatusInfo, RagStatusInfo } from '@/features/generation/composables/useGeneration';

const props = defineProps<{
  isGenerating: boolean;
  completed: number;
  total: number;
  currentSection: string;
  ragStatus: RagStatusInfo | null;
  assetStatus: AssetStatusInfo | null;
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
  if (action === 'expand') return '补充展开';
  if (action === 'simplify') return '压缩表达';
  return '改写';
}

const ragStatusClass = computed(() => (props.ragStatus ? `rag-${props.ragStatus.status}` : ''));
const assetStatusClass = computed(() => (props.assetStatus ? `asset-${props.assetStatus.status}` : ''));
</script>

<template>
  <div class="editor-status-stack">
    <div v-if="noticeText" class="generation-banner" :class="{ success: noticeTone === 'success' }">
      {{ noticeText }}
    </div>

    <div v-if="isGenerating" class="generation-banner generating">
      <span>
        正在整理 {{ currentSection || '内容' }}
        <template v-if="total">（{{ completed }}/{{ total }}）</template>
      </span>
      <button class="button ghost stop-btn" type="button" @click="$emit('stop')">停止整理</button>
    </div>

    <div v-if="ragStatus" class="generation-banner rag-banner" :class="ragStatusClass">
      <span class="rag-dot" />
      <span class="rag-message">{{ ragStatus.message }}</span>
      <span v-if="ragStatus.domain && ragStatus.retrieved_count" class="rag-meta">
        {{ ragStatus.domain }} · {{ ragStatus.retrieved_count }}/{{ ragStatus.chunk_count }} 条
      </span>
    </div>

    <div v-if="assetStatus" class="generation-banner asset-banner" :class="assetStatusClass">
      <span class="asset-dot" />
      <span class="rag-message">{{ assetStatus.message }}</span>
      <span v-if="assetStatus.status === 'ready'" class="rag-meta">
        我的资料 · {{ assetStatus.matched_assets.length }} 份 · {{ assetStatus.snippet_count }} 段
      </span>
    </div>

    <div v-if="isRewriting" class="generation-banner secondary">
      正在{{ getRewriteLabel(rewriteAction) }}当前内容
    </div>

    <div v-if="streamError" class="feedback">{{ streamError }}</div>
  </div>
</template>

<style scoped>
.stop-btn {
  margin-left: 12px;
  padding: 4px 10px;
  font-size: 0.8125rem;
  border: 1px solid var(--border);
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--text-secondary);
}

.stop-btn:hover {
  color: var(--danger);
  border-color: rgba(var(--danger-rgb), 0.28);
  background: rgba(var(--danger-rgb), 0.06);
}

.rag-banner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rag-dot {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  background: var(--text-secondary);
  flex: 0 0 auto;
}

.asset-banner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.asset-dot {
  width: 7px;
  height: 7px;
  border-radius: 9999px;
  background: var(--text-secondary);
  flex: 0 0 auto;
}

.asset-ready .asset-dot {
  background: var(--primary);
}

.asset-degraded .asset-dot {
  background: var(--warning);
}

.rag-ready .rag-dot {
  background: var(--success);
}

.rag-degraded .rag-dot,
.rag-matched_empty .rag-dot {
  background: var(--warning);
}

.rag-message {
  min-width: 0;
  flex: 1;
}

.rag-meta {
  color: var(--text-secondary);
  font-size: 0.8125rem;
  white-space: nowrap;
}
</style>
