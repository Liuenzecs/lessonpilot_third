<script setup lang="ts">
import type { TaskRecord } from '@/features/task/types';

defineProps<{
  task: TaskRecord | null;
  saveState: 'saved' | 'dirty' | 'saving' | 'retrying' | 'error' | 'conflict';
  outlineCollapsed: boolean;
  exportMenuOpen: boolean;
  hasMultipleDocs: boolean;
  currentDocType: 'lesson_plan' | 'study_guide';
  qualityReadiness: 'ready' | 'needs_fixes' | 'blocked' | null;
  qualityChecking: boolean;
}>();

defineEmits<{
  back: [];
  'toggle-outline': [];
  'open-history': [];
  'toggle-export-menu': [];
  export: [format: 'docx' | 'pptx'];
  'export-all': [];
  'open-export-preview': [];
  'quality-check': [];
  refresh: [];
  'retry-save': [];
}>();

function getSaveLabel(
  saveState: 'saved' | 'dirty' | 'saving' | 'retrying' | 'error' | 'conflict',
) {
  if (saveState === 'saved') {
    return '已保存';
  }
  if (saveState === 'saving') {
    return '保存中...';
  }
  if (saveState === 'retrying') {
    return '正在重试...';
  }
  if (saveState === 'dirty') {
    return '未保存的更改';
  }
  if (saveState === 'error') {
    return '未同步';
  }
  return '版本冲突';
}

function getQualityLabel(readiness: 'ready' | 'needs_fixes' | 'blocked' | null, checking: boolean) {
  if (checking) return '体检中...';
  if (readiness === 'ready') return '体检通过';
  if (readiness === 'needs_fixes') return '有提交提醒';
  if (readiness === 'blocked') return '有阻断项';
  return '导出前体检';
}
</script>

<template>
  <header class="editor-shell-header app-card">
    <div class="editor-shell-header-main">
      <div class="editor-shell-header-nav">
        <button class="button ghost" type="button" @click="$emit('back')">返回备课台</button>
        <button class="button ghost" type="button" @click="$emit('toggle-outline')">
          {{ outlineCollapsed ? '展开大纲' : '收起大纲' }}
        </button>
      </div>

      <div class="editor-shell-title-group">
        <div class="editor-shell-kicker">备课文档</div>
        <h1 class="editor-shell-title">{{ task?.title || '文档编辑器' }}</h1>
        <div class="editor-shell-meta">
          <span>{{ task?.subject || '未设置学科' }}</span>
          <span>·</span>
          <span>{{ task?.grade || '未设置年级' }}</span>
          <span>·</span>
          <span>{{ task?.topic || '未设置主题' }}</span>
          <template v-if="hasMultipleDocs">
            <span>·</span>
            <span>教案 + 学案双文档</span>
          </template>
        </div>
      </div>
    </div>

    <div class="editor-shell-actions">
      <div class="editor-save-stack">
        <div
          class="save-indicator"
          :class="{
            conflict: saveState === 'conflict',
            error: saveState === 'error',
            retrying: saveState === 'retrying',
          }"
        >
          {{ getSaveLabel(saveState) }}
        </div>

        <div v-if="saveState === 'conflict' || saveState === 'error'" class="editor-conflict-actions">
          <button v-if="saveState === 'conflict'" class="button ghost" type="button" @click="$emit('refresh')">
            刷新最新版本
          </button>
          <button class="button secondary" type="button" @click="$emit('retry-save')">重试保存</button>
        </div>
      </div>

      <button class="button secondary" type="button" @click="$emit('open-history')">历史版本</button>
      <button
        class="button secondary quality-check-button"
        type="button"
        :class="qualityReadiness ? `quality-${qualityReadiness}` : ''"
        :disabled="qualityChecking"
        @click="$emit('quality-check')"
      >
        {{ getQualityLabel(qualityReadiness, qualityChecking) }}
      </button>

      <div class="export-dropdown">
        <button class="button primary" type="button" @click="$emit('toggle-export-menu')">导出 ▾</button>
        <div v-if="exportMenuOpen" class="export-menu editor-export-menu">
          <div class="export-menu-title">导出为</div>
          <button class="menu-button" type="button" @click="$emit('export', 'docx')">
            Word 文档 (.docx)
          </button>
          <button v-if="currentDocType === 'lesson_plan'" class="menu-button" type="button" @click="$emit('export', 'pptx')">
            课堂课件 (.pptx)
          </button>
          <button v-if="hasMultipleDocs" class="menu-button" type="button" @click="$emit('export-all')">
            导出全部（教案 + 学案）
          </button>
          <button class="menu-button" type="button" @click="$emit('open-export-preview')">预览导出效果</button>
        </div>
      </div>
    </div>
  </header>
</template>
