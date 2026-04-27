<script setup lang="ts">
import type { QualityCheckResponse, QualityIssue } from '@/features/editor/types';

defineProps<{
  open: boolean;
  result: QualityCheckResponse | null;
  loading: boolean;
  fixing: boolean;
}>();

defineEmits<{
  close: [];
  export: [];
  fix: [issue: QualityIssue];
}>();

const readinessLabels = {
  ready: '可以导出',
  needs_fixes: '建议先处理',
  blocked: '暂不建议导出',
};

function issueKey(issue: QualityIssue, index: number) {
  return `${issue.section || 'document'}-${issue.message}-${index}`;
}

function canFixIssue(issue: QualityIssue) {
  return Boolean(issue.section && ['objectives', 'key_points', 'teaching_process', 'learning_objectives', 'assessment'].includes(issue.section));
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
            <button
              v-if="canFixIssue(issue)"
              class="quality-fix-btn"
              type="button"
              :disabled="fixing"
              @click="$emit('fix', issue)"
            >
              {{ fixing ? '正在调整...' : '按建议调整' }}
            </button>
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
            <button
              v-if="canFixIssue(warning)"
              class="quality-fix-btn"
              type="button"
              :disabled="fixing"
              @click="$emit('fix', warning)"
            >
              {{ fixing ? '正在调整...' : '按建议调整' }}
            </button>
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
            <button
              v-if="canFixIssue(suggestion)"
              class="quality-fix-btn"
              type="button"
              :disabled="fixing"
              @click="$emit('fix', suggestion)"
            >
              {{ fixing ? '正在调整...' : '按建议调整' }}
            </button>
          </div>
        </section>

        <section v-if="result.alignment_map.length" class="quality-group">
          <h4>目标-过程-评价</h4>
          <div
            v-for="item in result.alignment_map"
            :key="item.objective"
            class="quality-issue"
            :class="item.status === 'covered' ? 'suggestion' : 'warning'"
          >
            <strong>{{ item.objective }}</strong>
            <span>
              过程：{{ item.process_matches.join('、') || '未明显对应' }}；
              评价：{{ item.assessment_matches.join('、') || '未明显对应' }}
            </span>
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
