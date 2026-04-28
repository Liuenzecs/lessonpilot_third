<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  useConfirmSchoolTemplateMutation,
  useDeleteSchoolTemplateMutation,
  usePreviewSchoolTemplateMutation,
  useSchoolTemplates,
} from '@/features/task/composables/useTasks';
import type { SchoolTemplatePreview } from '@/features/task/types';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';

import '@/features/task/styles/workspace.css';

const router = useRouter();
const toast = useToast();
const templatesQuery = useSchoolTemplates();
const previewMutation = usePreviewSchoolTemplateMutation();
const confirmMutation = useConfirmSchoolTemplateMutation();
const deleteMutation = useDeleteSchoolTemplateMutation();

const preview = ref<SchoolTemplatePreview | null>(null);
const templateName = ref('');
const selectedFileName = ref('');
const uploadError = ref('');

const canSave = computed(() => Boolean(preview.value && templateName.value.trim()));

async function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  selectedFileName.value = file.name;
  uploadError.value = '';
  try {
    const result = await previewMutation.mutateAsync(file);
    preview.value = result;
    templateName.value = result.name;
    toast.success('已识别学校模板', '请检查字段和栏目后保存。');
  } catch (error) {
    preview.value = null;
    uploadError.value = getErrorDescription(error, '模板识别失败，请确认文件格式。');
    toast.error('模板识别失败', uploadError.value);
  } finally {
    input.value = '';
  }
}

async function saveTemplate() {
  if (!preview.value) return;
  try {
    await confirmMutation.mutateAsync({
      preview: preview.value,
      name: templateName.value.trim(),
    });
    toast.success('学校模板已保存', '导出 Word 时可以选择这个模板。');
    preview.value = null;
    templateName.value = '';
  } catch (error) {
    toast.error('保存模板失败', getErrorDescription(error, '请稍后重试。'));
  }
}

async function deleteTemplate(templateId: string) {
  if (!window.confirm('确认删除这个学校模板吗？')) return;
  try {
    await deleteMutation.mutateAsync(templateId);
    toast.success('模板已删除');
  } catch (error) {
    toast.error('删除模板失败', getErrorDescription(error, '请稍后重试。'));
  }
}
</script>

<template>
  <div class="page-shell create-page asset-page">
    <div class="create-frame app-card">
      <div class="create-head import-head">
        <button class="button ghost" type="button" @click="router.push({ name: 'tasks' })">
          ← 返回备课台
        </button>
        <div class="create-head-copy">
          <p class="page-eyebrow">学校模板</p>
          <h1 class="page-title">记住学校 Word 格式</h1>
          <p class="subtitle">上传学校常用模板，保存后导出教案时可直接套用栏目顺序和教学过程表格。</p>
        </div>
      </div>

      <div class="import-upload-band">
        <div>
          <h2>上传 .docx 模板</h2>
          <p>识别元信息、栏目顺序、教学过程表格和需要保留的空白区域。</p>
        </div>
        <label class="button primary import-file-button">
          {{ previewMutation.isPending.value ? '正在识别...' : '选择模板文件' }}
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

      <section v-if="preview" class="import-panel">
        <h2>模板预览</h2>
        <label class="create-field">
          <span class="create-label">模板名称</span>
          <input v-model.trim="templateName" class="create-input" type="text" />
        </label>

        <div class="asset-preview-grid">
          <div>
            <h3>字段映射</h3>
            <p v-for="item in preview.field_mappings" :key="`${item.template_label}-${item.content_field}`">
              {{ item.template_label }} → {{ item.content_field }}
            </p>
          </div>
          <div>
            <h3>栏目顺序</h3>
            <p>{{ preview.section_order.join(' / ') || '未识别到清晰栏目' }}</p>
          </div>
          <div>
            <h3>表格列</h3>
            <p v-for="layout in preview.table_layouts" :key="layout.name">
              {{ layout.name }}：{{ layout.columns.join(' / ') }}
            </p>
          </div>
          <div>
            <h3>保留空白</h3>
            <p>{{ preview.blank_areas.join(' / ') || '无' }}</p>
          </div>
        </div>

        <div v-if="preview.warnings.length" class="import-warning-list">
          <div v-for="warning in preview.warnings" :key="warning" class="import-warning">{{ warning }}</div>
        </div>

        <div class="create-foot">
          <button class="button ghost" type="button" @click="preview = null">重新选择</button>
          <button class="button primary" type="button" :disabled="!canSave || confirmMutation.isPending.value" @click="saveTemplate">
            {{ confirmMutation.isPending.value ? '正在保存...' : '保存为个人模板' }}
          </button>
        </div>
      </section>

      <section class="import-panel">
        <h2>我的学校模板</h2>
        <p v-if="templatesQuery.isLoading.value" class="create-helper">正在读取模板...</p>
        <p v-else-if="!(templatesQuery.data.value ?? []).length" class="create-helper">还没有保存学校模板。</p>
        <div v-else class="asset-card-grid">
          <article v-for="template in templatesQuery.data.value" :key="template.id" class="asset-card">
            <h3>{{ template.name }}</h3>
            <p>{{ template.subject }} · {{ template.grade || '通用年级' }}</p>
            <button class="button ghost" type="button" @click="deleteTemplate(template.id)">删除</button>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>
