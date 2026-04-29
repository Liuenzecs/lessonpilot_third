<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';

import { usePostCommentMutation, useSharedDocument } from '@/features/sharing/composables/useSharing';
import type { SharedDocumentView } from '@/features/sharing/types';
import { ApiError } from '@/shared/api/client';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';

const route = useRoute();
const toast = useToast();

const token = computed(() => route.params.token as string);
const enabled = computed(() => Boolean(token.value));

const { data: sharedDoc, isLoading, isError, error } = useSharedDocument(token, enabled);
const commentMutation = usePostCommentMutation(token);

const errorState = computed(() => {
  if (!isError.value || !error.value) return null;
  if (error.value instanceof ApiError) {
    if (error.value.status === 404) return { icon: '🔗', title: '链接不存在', description: '该分享链接可能已被删除，或地址有误。' };
    if (error.value.status === 410) return { icon: '⏰', title: '链接已过期', description: '该分享链接已超过有效期限，请联系分享者重新分享。' };
    if (error.value.status === 403) return { icon: '🔒', title: '分享已停用', description: '分享者已停用该链接，如需查看请联系分享者。' };
  }
  return { icon: '🔗', title: '无法访问', description: '分享链接不存在、已过期或已被停用。' };
});

const newCommentBody = ref('');
const newCommentAuthor = ref('');
const newCommentSubmitting = ref(false);

const canComment = computed(() => sharedDoc.value?.permission === 'comment');

async function submitComment() {
  if (!newCommentBody.value.trim()) return;
  newCommentSubmitting.value = true;
  try {
    await commentMutation.mutateAsync({
      body: newCommentBody.value.trim(),
      author_name: newCommentAuthor.value.trim() || undefined,
    });
    newCommentBody.value = '';
    toast.success('评论已提交');
  } catch (error) {
    toast.error('评论提交失败', getErrorDescription(error));
  } finally {
    newCommentSubmitting.value = false;
  }
}

function renderTextContent(text: string) {
  if (!text) return '（暂无内容）';
  return text;
}

function renderListItems(items: Array<{ content?: string; dimension?: string; prompt?: string }> | string[]) {
  if (!items?.length) return '（暂无内容）';
  return items.map((item) => {
    if (typeof item === 'string') return item;
    if (item.dimension && item.content) return `【${item.dimension}】${item.content}`;
    if (item.prompt) return item.prompt;
    return JSON.stringify(item);
  });
}

const sectionLabels: Record<string, string> = {
  header: '基本信息',
  objectives: '教学目标',
  key_points: '教学重难点',
  preparation: '教学准备',
  teaching_process: '教学过程',
  board_design: '板书设计',
  reflection: '教学反思',
  learning_objectives: '学习目标',
  key_difficulties: '重点难点预测',
  prior_knowledge: '知识链接',
  learning_process: '学习流程',
  assessment: '达标测评',
  extension: '拓展延伸',
  self_reflection: '自主反思',
};
</script>

<template>
  <div class="shared-doc-page">
    <header class="shared-doc-header">
      <div class="shared-doc-brand">LessonPilot</div>
      <div class="shared-doc-badge" :class="sharedDoc?.permission">
        {{ sharedDoc?.permission === 'comment' ? '可评论' : '只读' }}
      </div>
    </header>

    <div v-if="isLoading" class="shared-doc-loading">加载中...</div>

    <StatePanel
      v-else-if="errorState"
      :icon="errorState.icon"
      :title="errorState.title"
      :description="errorState.description"
      tone="error"
    />

    <main v-else class="shared-doc-main">
      <div class="shared-doc-meta">
        <h1 class="shared-doc-title">{{ sharedDoc?.title }}</h1>
        <p class="shared-doc-info">{{ sharedDoc?.subject }} · {{ sharedDoc?.grade }}{{ sharedDoc?.topic ? ` · ${sharedDoc?.topic}` : '' }}</p>
      </div>

      <!-- Section rendering -->
      <div class="shared-doc-sections">
        <template v-for="(value, key) in sharedDoc?.content" :key="key">
          <section
            v-if="!key.endsWith('_status') && !key.startsWith('section_') && key !== 'doc_type' && value != null && value !== ''"
            class="shared-section"
          >
            <h3 class="shared-section-title">{{ sectionLabels[key] ?? key }}</h3>

            <!-- String content -->
            <p v-if="typeof value === 'string'" class="shared-section-text">{{ renderTextContent(value) }}</p>

            <!-- Array of strings -->
            <ul v-else-if="Array.isArray(value) && value.length && typeof value[0] === 'string'" class="shared-section-list">
              <li v-for="(item, i) in (value as string[])" :key="i">{{ item }}</li>
            </ul>

            <!-- Array of objects (e.g. objectives, teaching_process steps) -->
            <div v-else-if="Array.isArray(value) && value.length && typeof value[0] === 'object'" class="shared-section-array">
              <div v-for="(item, i) in value" :key="i" class="shared-section-item">
                <template v-if="item.phase">
                  <h4 class="shared-step-phase">{{ item.phase }}{{ item.duration ? `（${item.duration}分钟）` : '' }}</h4>
                  <p v-if="item.teacher_activity"><strong>教师活动：</strong>{{ item.teacher_activity }}</p>
                  <p v-if="item.student_activity"><strong>学生活动：</strong>{{ item.student_activity }}</p>
                  <p v-if="item.design_intent"><strong>设计意图：</strong>{{ item.design_intent }}</p>
                </template>
                <template v-else-if="item.content">
                  <p>{{ item.content }}</p>
                </template>
                <template v-else-if="item.prompt">
                  <p>{{ item.prompt }}{{ item.answer ? ` — 答案：${item.answer}` : '' }}</p>
                </template>
              </div>
            </div>

            <!-- Object content (e.g. header, key_points) -->
            <div v-else-if="typeof value === 'object' && !Array.isArray(value)" class="shared-section-object">
              <template v-for="(v, k) in (value as Record<string, unknown>)" :key="k">
                <p v-if="typeof v === 'string' && v"><strong>{{ k }}：</strong>{{ v }}</p>
                <div v-else-if="Array.isArray(v) && v.length">
                  <p><strong>{{ k }}：</strong></p>
                  <ul>
                    <li v-for="(item, i) in (v as string[])" :key="i">{{ item }}</li>
                  </ul>
                </div>
              </template>
            </div>
          </section>
        </template>
      </div>

      <!-- Comments section -->
      <div v-if="canComment || sharedDoc?.comments.length" class="shared-comments">
        <h3 class="shared-comments-title">评论 ({{ sharedDoc?.comments.length }})</h3>

        <div v-for="comment in sharedDoc?.comments" :key="comment.id" class="comment-item">
          <div class="comment-header">
            <span class="comment-author">{{ comment.author_name }}</span>
            <span class="comment-time">{{ new Date(comment.created_at).toLocaleString() }}</span>
          </div>
          <p class="comment-body">{{ comment.body }}</p>
        </div>

        <!-- New comment form -->
        <div v-if="canComment" class="comment-form">
          <input
            v-model="newCommentAuthor"
            class="input"
            type="text"
            placeholder="你的名字（选填）"
            maxlength="50"
          />
          <textarea
            v-model="newCommentBody"
            class="input textarea"
            rows="3"
            placeholder="写下你的评论..."
            maxlength="2000"
          />
          <button
            class="button primary"
            type="button"
            :disabled="!newCommentBody.trim() || newCommentSubmitting"
            @click="submitComment"
          >
            {{ newCommentSubmitting ? '提交中...' : '提交评论' }}
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import StatePanel from '@/shared/components/StatePanel.vue';
export default { components: { StatePanel } };
</script>

<style scoped>
.shared-doc-page {
  min-height: 100vh;
  background: var(--color-bg);
}
.shared-doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}
.shared-doc-brand {
  font-weight: 700;
  font-size: 16px;
}
.shared-doc-badge {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 4px;
  background: var(--color-primary-light, #e8f4f8);
  color: var(--color-primary);
}
.shared-doc-badge.comment {
  background: var(--color-success-light, #e8f5e9);
  color: var(--color-success);
}
.shared-doc-loading {
  text-align: center;
  padding: 80px 0;
  color: var(--color-text-secondary);
}
.shared-doc-main {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px 80px;
}
.shared-doc-meta {
  margin-bottom: 32px;
}
.shared-doc-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
}
.shared-doc-info {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}
.shared-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border-light);
}
.shared-section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px;
  color: var(--color-primary);
}
.shared-section-text {
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  margin: 0;
}
.shared-section-list {
  margin: 0;
  padding-left: 20px;
  font-size: 14px;
  line-height: 1.7;
}
.shared-section-item {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--color-bg);
  border-radius: 6px;
}
.shared-section-item p {
  margin: 4px 0;
  font-size: 14px;
  line-height: 1.6;
}
.shared-step-phase {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 6px;
}
.shared-section-object p {
  margin: 4px 0;
  font-size: 14px;
}
.shared-comments {
  margin-top: 40px;
  padding-top: 24px;
  border-top: 2px solid var(--color-border);
}
.shared-comments-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
}
.comment-item {
  padding: 12px;
  margin-bottom: 12px;
  background: var(--color-bg);
  border-radius: 6px;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}
.comment-author {
  font-weight: 600;
  font-size: 13px;
}
.comment-time {
  font-size: 12px;
  color: var(--color-text-secondary);
}
.comment-body {
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
}
.textarea {
  resize: vertical;
  min-height: 80px;
}
</style>
