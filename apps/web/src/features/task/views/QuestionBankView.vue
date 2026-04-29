<script setup lang="ts">
import { onMounted } from 'vue';
import { useQuestionBank } from '@/features/task/composables/useQuestionBank';

const {
  chapters,
  questions,
  total,
  loading,
  error,
  selectedChapter,
  selectedDifficulty,
  selectedType,
  fetchChapters,
  fetchQuestions,
  typeLabel,
  difficultyLabel,
  difficultyClass,
} = useQuestionBank();

onMounted(() => {
  void fetchChapters();
  void fetchQuestions();
});

function clearFilters() {
  selectedChapter.value = null;
  selectedDifficulty.value = null;
  selectedType.value = null;
}
</script>

<template>
  <div class="qb-page">
    <header class="qb-header">
      <div class="qb-header-top">
        <button class="button ghost" type="button" @click="$router.push({ name: 'tasks' })">
          ← 返回备课台
        </button>
        <h1 class="qb-title">语文题库</h1>
      </div>
      <p class="qb-subtitle">
        语文 7-9 年级重点篇目分层题库，涵盖选择题、填空题和简答题，难度从 A 级（基础）到 D 级（选做）。
      </p>
    </header>

    <div class="qb-toolbar">
      <div class="qb-filters">
        <select v-model="selectedChapter" class="qb-select">
          <option :value="null">全部篇目</option>
          <option v-for="ch in chapters" :key="ch" :value="ch">{{ ch }}</option>
        </select>
        <select v-model="selectedDifficulty" class="qb-select">
          <option :value="null">全部难度</option>
          <option value="A">A级（基础）</option>
          <option value="B">B级（理解）</option>
          <option value="C">C级（拓展）</option>
          <option value="D">D级（选做）</option>
        </select>
        <select v-model="selectedType" class="qb-select">
          <option :value="null">全部题型</option>
          <option value="choice">选择题</option>
          <option value="fill_blank">填空题</option>
          <option value="short_answer">简答题</option>
        </select>
        <button
          v-if="selectedChapter || selectedDifficulty || selectedType"
          class="button ghost qb-clear"
          type="button"
          @click="clearFilters"
        >
          清除筛选
        </button>
      </div>
      <span class="qb-count">共 {{ total }} 道题目</span>
    </div>

    <div v-if="loading" class="qb-loading">加载中...</div>
    <div v-else-if="error" class="qb-error">{{ error }}</div>
    <div v-else-if="questions.length === 0" class="qb-empty">
      <p>暂无题目数据。请在服务端加载种子题库后刷新页面。</p>
    </div>

    <ul v-else class="qb-list">
      <li v-for="q in questions" :key="q.id" class="qb-card">
        <div class="qb-card-head">
          <span class="qb-chapter">{{ q.chapter }}</span>
          <span class="qb-grade">{{ q.grade }}</span>
          <span class="qb-tag" :class="difficultyClass[q.difficulty]">{{ difficultyLabel[q.difficulty] || q.difficulty }}</span>
          <span class="qb-tag qb-type">{{ typeLabel[q.question_type] || q.question_type }}</span>
          <span v-if="q.source && q.source !== '原创'" class="qb-source">{{ q.source }}</span>
        </div>
        <p class="qb-prompt">{{ q.prompt }}</p>
        <div v-if="q.options && q.options.length > 0" class="qb-options">
          <span v-for="(opt, i) in q.options" :key="i" class="qb-option">
            {{ String.fromCharCode(65 + i) }}. {{ opt }}
          </span>
        </div>
        <div class="qb-answer">
          <span class="qb-answer-label">参考答案：</span>{{ q.answer }}
        </div>
        <div v-if="q.analysis" class="qb-analysis">
          <span class="qb-analysis-label">解析：</span>{{ q.analysis }}
        </div>
        <div v-if="q.tags && q.tags.length > 0" class="qb-tags">
          <span v-for="tag in q.tags" :key="tag" class="qb-tag qb-tag-sm">{{ tag }}</span>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.qb-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px;
}

.qb-header {
  margin-bottom: 24px;
}

.qb-header-top {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.qb-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-ink, #172033);
  margin: 0;
}

.qb-subtitle {
  color: var(--color-muted, #64748b);
  font-size: 0.875rem;
  margin: 0;
}

.qb-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.qb-filters {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.qb-select {
  padding: 6px 12px;
  border: 1px solid var(--color-line, #d8dee8);
  border-radius: 6px;
  font-size: 0.875rem;
  background: #fff;
  color: var(--color-ink, #172033);
  max-width: 180px;
}

.qb-clear {
  font-size: 0.8rem;
}

.qb-count {
  font-size: 0.8rem;
  color: var(--color-muted, #64748b);
}

.qb-loading,
.qb-error,
.qb-empty {
  text-align: center;
  padding: 48px 0;
  color: var(--color-muted, #64748b);
}

.qb-empty-hint {
  font-size: 0.8rem;
  margin-top: 8px;
  opacity: 0.7;
}

.qb-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.qb-card {
  background: #fff;
  border: 1px solid var(--color-line, #d8dee8);
  border-radius: 8px;
  padding: 16px 20px;
}

.qb-card-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.qb-chapter {
  font-weight: 600;
  color: var(--color-ink, #172033);
  font-size: 0.9rem;
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.qb-grade {
  font-size: 0.8rem;
  color: var(--color-muted, #64748b);
}

.qb-tag {
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--color-desk-bg, #f4f6f8);
  color: var(--color-muted, #64748b);
}

.qb-tag.level-a { background: #dcfce7; color: #166534; }
.qb-tag.level-b { background: #dbeafe; color: #1e40af; }
.qb-tag.level-c { background: #fef3c7; color: #92400e; }
.qb-tag.level-d { background: #fce7f3; color: #9d174d; }

.qb-type {
  background: var(--color-desk-bg, #f4f6f8);
  color: var(--color-muted, #64748b);
}

.qb-source {
  font-size: 0.72rem;
  color: var(--color-teaching-blue, #2563eb);
}

.qb-prompt {
  margin: 0 0 8px;
  line-height: 1.7;
  color: var(--color-ink, #172033);
  font-size: 0.95rem;
}

.qb-options {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
  padding-left: 16px;
}

.qb-option {
  font-size: 0.875rem;
  color: var(--color-muted, #64748b);
}

.qb-answer {
  font-size: 0.85rem;
  color: var(--color-ready-green, #15803d);
  margin-bottom: 4px;
}

.qb-answer-label {
  font-weight: 600;
}

.qb-analysis {
  font-size: 0.85rem;
  color: var(--color-muted, #64748b);
  margin-bottom: 8px;
  line-height: 1.6;
}

.qb-analysis-label {
  font-weight: 600;
}

.qb-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.qb-tag-sm {
  font-size: 0.7rem;
  padding: 1px 6px;
}
</style>
