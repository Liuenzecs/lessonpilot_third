<script setup lang="ts">
import type { Block } from '@lessonpilot/shared-types';

import type { TaskRecord } from '@/features/task/types';

import BlockPreview from '@/features/editor/components/BlockPreview.vue';

defineProps<{
  open: boolean;
  task: TaskRecord | null;
  blocks: Block[];
}>();

defineEmits<{
  close: [];
}>();
</script>

<template>
  <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
    <div class="export-preview-modal app-card">
      <div class="export-preview-header">
        <div>
          <h3 style="margin: 0">预览导出效果</h3>
          <div class="muted">仅展示当前已确认内容，排版风格接近最终文档。</div>
        </div>
        <button class="button ghost" type="button" @click="$emit('close')">关闭</button>
      </div>

      <div class="export-preview-paper">
        <h1 class="export-preview-title">{{ task?.title || '教案预览' }}</h1>
        <div class="muted">{{ task?.subject || '未设置学科' }} · {{ task?.grade || '未设置年级' }} · {{ task?.topic || '未设置主题' }}</div>

        <div class="export-preview-body">
          <BlockPreview v-for="block in blocks" :key="block.id" :block="block" />
          <div v-if="blocks.length === 0" class="muted">当前还没有已确认内容可以导出。</div>
        </div>
      </div>
    </div>
  </div>
</template>
