<script setup lang="ts">
import type { QualityCheckResponse, QualityIssue } from '@/features/editor/types';

defineProps<{
  open: boolean;
  result: QualityCheckResponse | null;
  loading: boolean;
}>();

defineEmits<{
  close: [];
  export: [];
}>();

const readinessLabels = {
  ready: '可以导出',
  needs_fixes: '建议先处理',
  blocked: '暂不建议导出',
};

function issueKey(issue: QualityIssue, index: number) {
  return `${issue.section || 'document'}-${issue.message}-${index}`;
}
</script>

<template>
  <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
    <div class="quality-panel app-card">
      <div class="quality-panel-header">
        <div>
          <p class="page-eyebrow">导出前体检</p>
          <h3 class="quality-panel-title">
            {{ result ? readinessLabels[result.readiness] : '正在检查' }}
          </h3>
          <p class="quality-panel-summary">
            {{ loading ? '正在检查必填项、确认状态和教学过程完整度。' : result?.summary }}
          </p>
        </div>
        <button class="button ghost" type="button" @click="$emit('close')">关闭</button>
      </div>

      <div v-if="result" class="quality-panel-body">
        <section v-if="result.issues.length" class="quality-group">
          <h4>需要处理</h4>
          <div
            v-for="(issue, index) in result.issues"
            :key="issueKey(issue, index)"
            class="quality-issue"
            :class="issue.severity"
          >
            <strong>{{ issue.message }}</strong>
            <span>{{ issue.suggestion }}</span>
          </div>
        </section>

        <section v-if="result.warnings.length" class="quality-group">
          <h4>提醒</h4>
          <div
            v-for="(warning, index) in result.warnings"
            :key="issueKey(warning, index)"
            class="quality-issue warning"
          >
            <strong>{{ warning.message }}</strong>
            <span>{{ warning.suggestion }}</span>
          </div>
        </section>

        <section v-if="result.suggestions.length" class="quality-group">
          <h4>可选优化</h4>
          <div
            v-for="(suggestion, index) in result.suggestions"
            :key="issueKey(suggestion, index)"
            class="quality-issue suggestion"
          >
            <strong>{{ suggestion.message }}</strong>
            <span>{{ suggestion.suggestion }}</span>
          </div>
        </section>

        <div v-if="!result.issues.length && !result.warnings.length" class="quality-ready-box">
          当前文档已满足主要导出要求。
        </div>
      </div>

      <div class="quality-panel-actions">
        <button class="button ghost" type="button" @click="$emit('close')">稍后处理</button>
        <button
          class="button primary"
          type="button"
          :disabled="loading || result?.readiness === 'blocked'"
          @click="$emit('export')"
        >
          仍然导出 Word
        </button>
      </div>
    </div>
  </div>
</template>
