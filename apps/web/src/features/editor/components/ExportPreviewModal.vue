<script setup lang="ts">
import type { DocumentContent, SectionInfo } from '@lessonpilot/shared-types';

import type { TaskRecord } from '@/features/task/types';
import { computed } from 'vue';
import { getSections } from '@/shared/utils/content';
import StatePanel from '@/shared/components/StatePanel.vue';

const props = defineProps<{
  open: boolean;
  task: TaskRecord | null;
  content: DocumentContent | null;
}>();

defineEmits<{
  close: [];
}>();

const sections = computed<SectionInfo[]>(() =>
  props.content ? getSections(props.content) : [],
);

function getSectionText(sectionName: string): string {
  if (!props.content) return '';
  const data = (props.content as unknown as Record<string, unknown>)[sectionName];
  if (typeof data === 'string') return data;
  if (Array.isArray(data)) {
    return data.map((item) => {
      if (typeof item === 'string') return item;
      if (typeof item === 'object' && item !== null) {
        const obj = item as Record<string, unknown>;
        if (obj.content) return String(obj.content);
        if (obj.prompt) return String(obj.prompt);
        return JSON.stringify(item, null, 2);
      }
      return String(item);
    }).join('\n');
  }
  if (typeof data === 'object' && data !== null) {
    return JSON.stringify(data, null, 2);
  }
  return '';
}
</script>

<template>
  <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
    <div class="export-preview-modal app-card">
      <div class="export-preview-header">
        <div>
          <h3 class="export-preview-heading">预览导出效果</h3>
          <div class="muted">展示当前已确认的内容，排版接近最终文档。</div>
        </div>
        <button class="button ghost" type="button" @click="$emit('close')">关闭</button>
      </div>

      <div class="export-preview-paper">
        <div class="export-preview-paper-head">
          <h1 class="export-preview-title">{{ task?.title || '文档预览' }}</h1>
          <div class="export-preview-meta">
            {{ task?.subject || '未设置学科' }} · {{ task?.grade || '未设置年级' }} · {{ task?.topic || '未设置主题' }}
          </div>
        </div>

        <div class="export-preview-body">
          <template v-if="sections.length">
            <div v-for="section in sections" :key="section.name" class="preview-section">
              <h4 class="preview-section-title">{{ section.title }}</h4>
              <pre class="preview-section-content">{{ getSectionText(section.name) || '（空）' }}</pre>
            </div>
          </template>
          <StatePanel
            v-else
            icon="📄"
            title="当前还没有已确认内容可以导出"
            description="先接受建议内容或补充正文内容，再回来预览最终文档效果。"
            tone="empty"
            compact
          />
        </div>
      </div>
    </div>
  </div>
</template>
