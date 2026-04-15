<script setup lang="ts">
import type { DocumentContent, SectionInfo } from '@lessonpilot/shared-types';
import type { DocumentSnapshotRecord } from '@/features/editor/types';
import { computed } from 'vue';
import { getSections } from '@/shared/utils/content';

const props = defineProps<{
  open: boolean;
  loading: boolean;
  previewLoading: boolean;
  items: DocumentSnapshotRecord[];
  previewSnapshot: DocumentSnapshotRecord | null;
  selectedSnapshotId: string | null;
}>();

defineEmits<{
  close: [];
  select: [snapshotId: string];
  restore: [snapshotId: string];
}>();

function formatSource(source: string): string {
  if (source === 'save') return '普通保存';
  if (source === 'generation') return '自动生成';
  if (source === 'rewrite') return '重写';
  if (source === 'restore') return '历史恢复';
  return source;
}

const previewSections = computed<SectionInfo[]>(() =>
  props.previewSnapshot ? getSections(props.previewSnapshot.content) : [],
);

function getSectionText(content: DocumentContent, sectionName: string): string {
  const data = (content as unknown as Record<string, unknown>)[sectionName];
  if (typeof data === 'string') return data;
  if (Array.isArray(data)) {
    return data.map((item) => {
      if (typeof item === 'string') return item;
      if (typeof item === 'object' && item !== null) {
        const obj = item as Record<string, unknown>;
        if (obj.content) return String(obj.content);
        if (obj.prompt) return String(obj.prompt);
        return JSON.stringify(item);
      }
      return String(item);
    }).join('\n');
  }
  if (typeof data === 'object' && data !== null) return JSON.stringify(data, null, 2);
  return '';
}
</script>

<template>
  <div v-if="open" class="history-drawer-backdrop" @click.self="$emit('close')">
    <aside class="history-drawer app-card">
      <div class="history-drawer-header">
        <div>
          <h3 class="history-drawer-title">历史版本</h3>
          <div class="muted">最近 10 个可恢复快照。恢复后会生成一个新的当前版本。</div>
        </div>
        <button class="button ghost" type="button" @click="$emit('close')">关闭</button>
      </div>

      <div class="history-drawer-layout">
        <div class="history-list-panel">
          <div v-if="loading" class="muted">正在加载历史记录...</div>
          <button
            v-for="item in items"
            :key="item.id"
            class="history-item"
            :class="{ active: selectedSnapshotId === item.id }"
            type="button"
            @click="$emit('select', item.id)"
          >
            <div class="history-item-version">v{{ item.version }}</div>
            <div class="history-item-source">{{ formatSource(item.source) }}</div>
            <div class="history-item-time">{{ new Date(item.created_at).toLocaleString() }}</div>
          </button>
        </div>

        <div class="history-preview-panel">
          <div v-if="previewLoading" class="muted">正在加载快照预览...</div>

          <template v-else-if="previewSnapshot">
            <div class="history-preview-head">
              <div>
                <div class="history-preview-version">版本 v{{ previewSnapshot.version }}</div>
                <div class="muted">{{ formatSource(previewSnapshot.source) }}</div>
              </div>
              <button class="button primary" type="button" @click="$emit('restore', previewSnapshot.id)">
                恢复为当前新版本
              </button>
            </div>

            <div class="history-preview-body">
              <div v-for="section in previewSections" :key="section.name" class="preview-section">
                <h4 class="preview-section-title">{{ section.title }}</h4>
                <pre class="preview-section-text">{{ getSectionText(previewSnapshot.content, section.name) || '（空）' }}</pre>
              </div>
            </div>
          </template>

          <div v-else class="preview-hint">先从左侧选择一个历史快照，再预览或恢复。</div>
        </div>
      </div>
    </aside>
  </div>
</template>
