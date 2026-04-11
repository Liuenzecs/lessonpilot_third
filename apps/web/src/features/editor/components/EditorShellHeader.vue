<script setup lang="ts">
import type { TaskRecord } from '@/features/task/types';

defineProps<{
  task: TaskRecord | null;
  saveState: 'saved' | 'dirty' | 'saving' | 'conflict';
  outlineCollapsed: boolean;
  exportMenuOpen: boolean;
}>();

defineEmits<{
  back: [];
  'toggle-outline': [];
  'open-history': [];
  'toggle-export-menu': [];
  export: [format: 'docx' | 'pdf'];
  'open-export-preview': [];
  refresh: [];
}>();
</script>

<template>
  <header class="editor-shell-header app-card">
    <div class="editor-shell-header-main">
      <div class="button-row">
        <button class="button ghost" type="button" @click="$emit('back')">返回备课台</button>
        <button class="button ghost" type="button" @click="$emit('toggle-outline')">
          {{ outlineCollapsed ? '展开大纲' : '收起大纲' }}
        </button>
      </div>

      <div class="editor-shell-title-group">
        <h1 class="editor-shell-title">{{ task?.title || '教案编辑器' }}</h1>
        <div class="task-meta">
          {{ task?.subject || '未设置学科' }} · {{ task?.grade || '未设置年级' }} · {{ task?.topic || '未设置主题' }}
        </div>
      </div>
    </div>

    <div class="header-actions">
      <div class="save-indicator" :class="{ conflict: saveState === 'conflict' }">
        <template v-if="saveState === 'saved'">已保存</template>
        <template v-else-if="saveState === 'saving'">保存中...</template>
        <template v-else-if="saveState === 'dirty'">未保存的更改</template>
        <template v-else>保存冲突，请刷新或重试</template>
      </div>

      <button v-if="saveState === 'conflict'" class="button ghost" type="button" @click="$emit('refresh')">
        刷新最新版本
      </button>
      <button class="button secondary" type="button" @click="$emit('open-history')">历史版本</button>

      <div class="export-dropdown">
        <button class="button primary" type="button" @click="$emit('toggle-export-menu')">导出</button>
        <div v-if="exportMenuOpen" class="export-menu editor-export-menu">
          <div class="export-menu-title">导出为</div>
          <button class="menu-button" type="button" @click="$emit('export', 'docx')">Word 文档</button>
          <button class="menu-button" type="button" @click="$emit('export', 'pdf')">PDF 文档</button>
          <button class="menu-button" type="button" @click="$emit('open-export-preview')">预览导出效果</button>
        </div>
      </div>
    </div>
  </header>
</template>
