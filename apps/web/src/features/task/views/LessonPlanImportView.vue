<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  useConfirmLessonPlanImportMutation,
  usePreviewLessonPlanImportMutation,
} from '@/features/task/composables/useTasks';
import type { LessonPlanImportMetadata, LessonPlanImportPreview } from '@/features/task/types';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';
import {
  GRADE_OPTIONS,
  LESSON_CATEGORY_OPTIONS,
  SCENE_OPTIONS,
  SUBJECT_OPTIONS,
} from '@/shared/constants/options';

import '@/features/task/styles/workspace.css';

const router = useRouter();
const toast = useToast();
const previewMutation = usePreviewLessonPlanImportMutation();
const confirmMutation = useConfirmLessonPlanImportMutation();

const selectedFileName = ref('');
const preview = ref<LessonPlanImportPreview | null>(null);
const metadata = ref<LessonPlanImportMetadata | null>(null);
const uploadError = ref('');

const canConfirm = computed(() =>
  Boolean(preview.value && metadata.value?.subject && metadata.value?.grade && metadata.value?.topic),
);

const sectionLabels: Record<string, string> = {
  objectives: '教学目标',
  key_points: '教学重难点',
  preparation: '教学准备',
  teaching_process: '教学过程',
  board_design: '板书设计',
  reflection: '教学反思',
};

async function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  selectedFileName.value = file.name;
  uploadError.value = '';
  try {
    const result = await previewMutation.mutateAsync(file);
    preview.value = result;
    metadata.value = { ...result.metadata };
    toast.success('已识别 Word 教案', '请先检查栏目映射，再确认导入。');
  } catch (error) {
    preview.value = null;
    metadata.value = null;
    uploadError.value = getErrorDescription(error, '导入失败，请确认文件格式。');
    toast.error('导入失败', uploadError.value);
  } finally {
    input.value = '';
  }
}

async function confirmImport() {
  if (!preview.value || !metadata.value) return;
  try {
    const result = await confirmMutation.mutateAsync({
      metadata: metadata.value,
      content: preview.value.content,
    });
    toast.success('旧教案已导入', '已作为待确认内容放入编辑器。');
    await router.push({ name: 'editor', params: { taskId: result.task.id } });
  } catch (error) {
    toast.error('确认导入失败', getErrorDescription(error, '请稍后重试。'));
  }
}
</script>

<template>
  <div class="page-shell create-page import-page">
    <div class="create-frame app-card">
      <div class="create-head import-head">
        <button class="button ghost" type="button" @click="router.push({ name: 'tasks' })">
          ← 返回备课台
        </button>
        <div class="create-head-copy">
          <p class="page-eyebrow">旧教案导入</p>
          <h1 class="page-title">把 Word 教案带进来</h1>
          <p class="subtitle">先识别栏目和教学过程，确认后会作为待确认内容进入编辑器。</p>
        </div>
      </div>

      <div class="import-upload-band">
        <div>
          <h2>上传 .docx 教案</h2>
          <p>支持常见“教学目标、重难点、教学过程、板书设计、教学反思”结构。</p>
        </div>
        <label class="button primary import-file-button">
          {{ previewMutation.isPending.value ? '正在识别...' : '选择 Word 文件' }}
          <input
            type="file"
            accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            :disabled="previewMutation.isPending.value"
            @change="handleFileChange"
          />
        </label>
      </div>

      <p v-if="selectedFileName" class="create-helper">当前文件：{{ selectedFileName }}</p>
      <p v-if="uploadError" class="feedback">{{ uploadError }}</p>

      <div v-if="preview && metadata" class="import-preview-layout">
        <section class="import-panel">
          <h2>基本信息</h2>
          <div class="import-meta-grid">
            <label class="create-field">
              <span class="create-label">标题</span>
              <input v-model.trim="metadata.title" class="create-input" type="text" />
            </label>
            <label class="create-field">
              <span class="create-label">课题</span>
              <input v-model.trim="metadata.topic" class="create-input" type="text" />
            </label>
            <label class="create-field">
              <span class="create-label">学科</span>
              <select v-model="metadata.subject" class="create-input">
                <option v-for="subject in SUBJECT_OPTIONS" :key="subject" :value="subject">{{ subject }}</option>
              </select>
            </label>
            <label class="create-field">
              <span class="create-label">年级</span>
              <select v-model="metadata.grade" class="create-input">
                <option value="">请选择年级</option>
                <option v-for="grade in GRADE_OPTIONS" :key="grade" :value="grade">{{ grade }}</option>
              </select>
            </label>
            <label class="create-field">
              <span class="create-label">课时</span>
              <input v-model.number="metadata.class_hour" class="create-input" type="number" min="1" max="10" />
            </label>
            <label class="create-field">
              <span class="create-label">课型</span>
              <select v-model="metadata.lesson_category" class="create-input">
                <option v-for="item in LESSON_CATEGORY_OPTIONS" :key="item.value" :value="item.value">
                  {{ item.label }}
                </option>
              </select>
            </label>
            <label class="create-field">
              <span class="create-label">使用场景</span>
              <select v-model="metadata.scene" class="create-input">
                <option v-for="item in SCENE_OPTIONS" :key="item.value" :value="item.value">{{ item.label }}</option>
              </select>
            </label>
          </div>
        </section>

        <section class="import-panel">
          <h2>识别结果</h2>
          <div class="import-section-grid">
            <div
              v-for="name in preview.mapped_sections"
              :key="name"
              class="import-section-pill"
            >
              {{ sectionLabels[name] || name }}
            </div>
          </div>
          <div v-if="preview.warnings.length" class="import-warning-list">
            <div v-for="(warning, index) in preview.warnings" :key="index" class="import-warning">
              {{ warning.message }}
            </div>
          </div>
        </section>

        <section class="import-panel">
          <h2>正文预览</h2>
          <div class="import-preview-sections">
            <div class="preview-section">
              <h3>教学目标</h3>
              <p v-for="objective in preview.content.objectives" :key="objective.content">
                {{ objective.content }}
              </p>
            </div>
            <div class="preview-section">
              <h3>教学重难点</h3>
              <p v-for="item in preview.content.key_points.keyPoints" :key="item">重点：{{ item }}</p>
              <p v-for="item in preview.content.key_points.difficulties" :key="item">难点：{{ item }}</p>
            </div>
            <div class="preview-section">
              <h3>教学过程</h3>
              <p v-for="step in preview.content.teaching_process" :key="`${step.phase}-${step.teacher_activity}`">
                {{ step.phase }} · {{ step.duration }} 分钟 · {{ step.teacher_activity }}
              </p>
            </div>
            <div class="preview-section">
              <h3>板书设计</h3>
              <p>{{ preview.content.board_design || '（未识别）' }}</p>
            </div>
            <div class="preview-section">
              <h3>教学反思</h3>
              <p>{{ preview.content.reflection || '（未识别）' }}</p>
            </div>
          </div>
        </section>

        <section v-if="preview.unmapped_sections.length" class="import-panel">
          <h2>未识别内容</h2>
          <p class="create-helper">这些内容不会丢失，请确认是否需要手动放进某个 section。</p>
          <div class="import-unmapped-list">
            <pre v-for="(item, index) in preview.unmapped_sections" :key="index">{{ item.content }}</pre>
          </div>
        </section>

        <div class="create-foot">
          <button class="button ghost" type="button" @click="preview = null; metadata = null">重新选择</button>
          <button
            class="button primary"
            type="button"
            :disabled="!canConfirm || confirmMutation.isPending.value"
            @click="confirmImport"
          >
            {{ confirmMutation.isPending.value ? '正在导入...' : '确认导入并进入编辑器' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
