<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  useConfirmBatchImportMutation,
  usePreviewBatchImportMutation,
} from '@/features/task/composables/useTasks';
import type { LessonPlanImportMetadata, LessonPlanImportPreview } from '@/features/task/types';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';

const router = useRouter();
const toast = useToast();

const previewMutation = usePreviewBatchImportMutation();
const confirmMutation = useConfirmBatchImportMutation();

const selectedFiles = ref<File[]>([]);
const previews = ref<LessonPlanImportPreview[]>([]);
const editableMetadatas = ref<LessonPlanImportMetadata[]>([]);
const confirming = ref(false);

const hasPreviews = computed(() => previews.value.length > 0);
const anyProcessing = computed(() => previewMutation.isPending.value || confirming.value);

function handleFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) return;
  selectedFiles.value = Array.from(input.files);
  previews.value = [];
  editableMetadatas.value = [];
}

async function previewAll() {
  if (!selectedFiles.value.length) return;
  try {
    const result = await previewMutation.mutateAsync(selectedFiles.value);
    previews.value = result.items;
    editableMetadatas.value = result.items.map((item) => ({ ...item.metadata }));
    toast.success(`已预览 ${result.items.length} 份教案`);
  } catch (error) {
    toast.error('预览失败', getErrorDescription(error, '请检查文件格式后重试。'));
  }
}

function updateMetadata(index: number, field: keyof LessonPlanImportMetadata, value: unknown) {
  editableMetadatas.value[index] = {
    ...editableMetadatas.value[index],
    [field]: value,
  };
}

function removeItem(index: number) {
  previews.value.splice(index, 1);
  editableMetadatas.value.splice(index, 1);
}

async function confirmAll() {
  if (!previews.value.length) return;
  confirming.value = true;
  try {
    const result = await confirmMutation.mutateAsync({
      items: previews.value.map((preview, i) => ({
        metadata: editableMetadatas.value[i] ?? preview.metadata,
        content: preview.content,
      })),
    });
    toast.success(`成功导入 ${result.succeeded} 份${result.failed > 0 ? `，${result.failed} 份失败` : ''}`);
    if (result.failed > 0) {
      for (const f of result.failures) {
        toast.error(`「${f.source_filename}」导入失败`, f.error);
      }
    }
    if (result.items.length > 0) {
      const firstId = result.items[0].task.id;
      router.push({ name: 'editor', params: { taskId: firstId } });
    }
  } catch (error) {
    toast.error('批量导入确认失败', getErrorDescription(error, '请稍后重试。'));
  } finally {
    confirming.value = false;
  }
}

const sectionLabels: Record<string, string> = {
  objectives: '教学目标',
  key_points: '教学重难点',
  preparation: '教学准备',
  teaching_process: '教学过程',
  board_design: '板书设计',
  reflection: '教学反思',
};
</script>

<template>
  <div class="page-shell">
    <header class="page-header">
      <button class="button ghost" type="button" @click="router.push({ name: 'tasks' })">← 返回备课台</button>
      <h1 class="page-title">批量导入旧教案</h1>
      <p class="page-subtitle">一次选择多个 .docx 文件，预览后确认导入</p>
    </header>

    <div class="batch-import-body">
      <!-- Step 1: File selection -->
      <section class="batch-step">
        <h2 class="batch-step-title">1. 选择文件</h2>
        <label class="file-picker">
          <span>选择 Word 文件（可多选，最多 10 个）</span>
          <input
            type="file"
            accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            multiple
            :disabled="anyProcessing"
            @change="handleFilesSelected"
          />
        </label>
        <ul v-if="selectedFiles.length" class="file-list">
          <li v-for="(f, i) in selectedFiles" :key="i" class="file-item">
            <span class="file-name">{{ f.name }}</span>
            <span class="file-size">{{ (f.size / 1024).toFixed(0) }} KB</span>
          </li>
        </ul>
        <button
          v-if="selectedFiles.length && !hasPreviews"
          class="button primary"
          type="button"
          :disabled="previewMutation.isPending.value"
          @click="previewAll"
        >
          {{ previewMutation.isPending.value ? '解析中...' : '全部预览' }}
        </button>
      </section>

      <!-- Step 2: Preview & edit -->
      <section v-if="hasPreviews" class="batch-step">
        <h2 class="batch-step-title">2. 逐项确认（{{ previews.length }} 份）</h2>

        <div v-for="(preview, idx) in previews" :key="idx" class="preview-card app-card">
          <div class="preview-card-header">
            <div class="preview-card-meta">
              <span class="preview-filename">{{ preview.source_filename }}</span>
              <span v-if="preview.warnings.length" class="badge warning">{{ preview.warnings.length }} 个提醒</span>
            </div>
            <button class="button ghost danger" type="button" @click="removeItem(idx)">移除</button>
          </div>

          <!-- Editable metadata -->
          <div class="meta-grid">
            <label class="meta-field">
              <span class="meta-label">标题</span>
              <input
                v-model="editableMetadatas[idx].title"
                class="input"
                type="text"
                :disabled="anyProcessing"
              />
            </label>
            <label class="meta-field">
              <span class="meta-label">学科</span>
              <input
                v-model="editableMetadatas[idx].subject"
                class="input"
                type="text"
                :disabled="anyProcessing"
              />
            </label>
            <label class="meta-field">
              <span class="meta-label">年级</span>
              <input
                v-model="editableMetadatas[idx].grade"
                class="input"
                type="text"
                :disabled="anyProcessing"
              />
            </label>
            <label class="meta-field">
              <span class="meta-label">课题</span>
              <input
                v-model="editableMetadatas[idx].topic"
                class="input"
                type="text"
                :disabled="anyProcessing"
              />
            </label>
            <label class="meta-field">
              <span class="meta-label">课时</span>
              <input
                v-model.number="editableMetadatas[idx].class_hour"
                class="input"
                type="number"
                min="1"
                max="10"
                :disabled="anyProcessing"
              />
            </label>
            <label class="meta-field">
              <span class="meta-label">课型</span>
              <select v-model="editableMetadatas[idx].lesson_category" class="input" :disabled="anyProcessing">
                <option value="new">新授课</option>
                <option value="review">复习课</option>
                <option value="exercise">练习课</option>
                <option value="comprehensive">综合课</option>
              </select>
            </label>
            <label class="meta-field">
              <span class="meta-label">使用场景</span>
              <select v-model="editableMetadatas[idx].scene" class="input" :disabled="anyProcessing">
                <option value="public_school">公立校</option>
                <option value="tutor">家教</option>
                <option value="institution">培训机构</option>
              </select>
            </label>
          </div>

          <!-- Recognized sections -->
          <div class="mapped-sections">
            <span class="mapped-label">已识别章节：</span>
            <span v-for="s in preview.mapped_sections" :key="s" class="badge mapped">
              {{ sectionLabels[s] ?? s }}
            </span>
            <span v-if="!preview.mapped_sections.length" class="text-muted">未识别到章节</span>
          </div>

          <!-- Warnings -->
          <div v-if="preview.warnings.length" class="warnings">
            <p v-for="(w, wi) in preview.warnings" :key="wi" class="warning-text">⚠ {{ w.message }}</p>
          </div>
        </div>

        <!-- Step 3: Confirm -->
        <div class="confirm-bar">
          <button
            class="button primary"
            type="button"
            :disabled="confirming"
            @click="confirmAll"
          >
            {{ confirming ? '导入中...' : `批量确认导入（${previews.length} 份）` }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.batch-import-body {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.batch-step {
  margin-bottom: 32px;
}

.batch-step-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px;
  color: var(--color-text);
}

.file-picker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  color: var(--color-text-secondary);
  font-size: 14px;
  transition: border-color 0.15s;
}
.file-picker:hover {
  border-color: var(--color-primary);
}
.file-picker input {
  display: none;
}

.file-list {
  list-style: none;
  padding: 0;
  margin: 12px 0 0;
}
.file-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}
.file-name { font-weight: 500; color: var(--color-text); }

.preview-card {
  padding: 20px;
  margin-bottom: 16px;
}
.preview-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.preview-filename {
  font-weight: 600;
  font-size: 14px;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}
.meta-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.meta-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.mapped-sections {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.mapped-label {
  color: var(--color-text-secondary);
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.badge.mapped {
  background: var(--color-primary-light, #e8f4f8);
  color: var(--color-primary);
}
.badge.warning {
  background: var(--color-warning-light, #fff3e0);
  color: var(--color-warning);
}

.warnings {
  margin-top: 8px;
}
.warning-text {
  font-size: 12px;
  color: var(--color-warning);
  margin: 2px 0;
}

.confirm-bar {
  text-align: center;
  margin-top: 24px;
}
</style>
