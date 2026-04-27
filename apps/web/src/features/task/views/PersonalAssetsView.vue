<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  useConfirmPersonalAssetMutation,
  useDeletePersonalAssetMutation,
  usePersonalAssets,
  usePreviewPersonalAssetMutation,
} from '@/features/task/composables/useTasks';
import type { PersonalAssetPreview } from '@/features/task/types';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';

import '@/features/task/styles/workspace.css';

const router = useRouter();
const toast = useToast();
const assetsQuery = usePersonalAssets();
const previewMutation = usePreviewPersonalAssetMutation();
const confirmMutation = useConfirmPersonalAssetMutation();
const deleteMutation = useDeletePersonalAssetMutation();

const preview = ref<PersonalAssetPreview | null>(null);
const assetTitle = ref('');
const selectedFileName = ref('');
const uploadError = ref('');

const canSave = computed(() => Boolean(preview.value && assetTitle.value.trim()));

const assetTypeLabels: Record<string, string> = {
  lesson_plan: '旧教案',
  study_guide: '学案/讲义',
  ppt_outline: 'PPT 大纲',
  teaching_note: '教学笔记',
  reference_material: '参考资料',
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
    assetTitle.value = result.title;
    toast.success('资料已识别', '请检查预览后保存到个人资料库。');
  } catch (error) {
    preview.value = null;
    uploadError.value = getErrorDescription(error, '资料识别失败，请确认文件格式。');
    toast.error('资料识别失败', uploadError.value);
  } finally {
    input.value = '';
  }
}

async function saveAsset() {
  if (!preview.value) return;
  try {
    await confirmMutation.mutateAsync({ preview: preview.value, title: assetTitle.value.trim() });
    toast.success('资料已保存', '后续可以作为个人备课资产复用。');
    preview.value = null;
    assetTitle.value = '';
  } catch (error) {
    toast.error('保存资料失败', getErrorDescription(error, '请稍后重试。'));
  }
}

async function deleteAsset(assetId: string) {
  if (!window.confirm('确认删除这份个人资料吗？')) return;
  try {
    await deleteMutation.mutateAsync(assetId);
    toast.success('资料已删除');
  } catch (error) {
    toast.error('删除资料失败', getErrorDescription(error, '请稍后重试。'));
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
          <p class="page-eyebrow">个人资料库</p>
          <h1 class="page-title">把旧讲义和 PPT 带进来</h1>
          <p class="subtitle">支持 .docx 和 .pptx，先预览识别结果，再保存为当前账号私有资料。</p>
        </div>
      </div>

      <div class="import-upload-band">
        <div>
          <h2>上传旧资料</h2>
          <p>旧教案、讲义、教学笔记和 PPT 大纲都可以先放进资料库。</p>
        </div>
        <label class="button primary import-file-button">
          {{ previewMutation.isPending.value ? '正在识别...' : '选择资料文件' }}
          <input
            type="file"
            accept=".docx,.pptx,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.presentationml.presentation"
            :disabled="previewMutation.isPending.value"
            @change="handleFileChange"
          />
        </label>
      </div>

      <p v-if="selectedFileName" class="create-helper">当前文件：{{ selectedFileName }}</p>
      <p v-if="uploadError" class="feedback">{{ uploadError }}</p>

      <section v-if="preview" class="import-panel">
        <h2>资料预览</h2>
        <label class="create-field">
          <span class="create-label">资料名称</span>
          <input v-model.trim="assetTitle" class="create-input" type="text" />
        </label>
        <div class="asset-preview-grid">
          <div>
            <h3>识别类型</h3>
            <p>{{ assetTypeLabels[preview.asset_type] }}</p>
          </div>
          <div>
            <h3>可复用建议</h3>
            <p v-for="item in preview.reuse_suggestions" :key="item.target">{{ item.label }}：{{ item.reason }}</p>
          </div>
        </div>
        <div class="import-preview-sections">
          <div v-for="section in preview.extracted_sections.slice(0, 6)" :key="`${section.title}-${section.content}`" class="preview-section">
            <h3>{{ section.title }}</h3>
            <p>{{ section.content || '（空白）' }}</p>
          </div>
        </div>
        <div v-if="preview.warnings.length" class="import-warning-list">
          <div v-for="warning in preview.warnings" :key="warning" class="import-warning">{{ warning }}</div>
        </div>
        <div class="create-foot">
          <button class="button ghost" type="button" @click="preview = null">重新选择</button>
          <button class="button primary" type="button" :disabled="!canSave || confirmMutation.isPending.value" @click="saveAsset">
            {{ confirmMutation.isPending.value ? '正在保存...' : '保存到资料库' }}
          </button>
        </div>
      </section>

      <section class="import-panel">
        <h2>我的资料</h2>
        <p v-if="assetsQuery.isLoading.value" class="create-helper">正在读取资料...</p>
        <p v-else-if="!(assetsQuery.data.value ?? []).length" class="create-helper">还没有保存个人资料。</p>
        <div v-else class="asset-card-grid">
          <article v-for="asset in assetsQuery.data.value" :key="asset.id" class="asset-card">
            <h3>{{ asset.title }}</h3>
            <p>{{ assetTypeLabels[asset.asset_type] || asset.asset_type }} · {{ asset.source_filename }}</p>
            <button class="button ghost" type="button" @click="deleteAsset(asset.id)">删除</button>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>
