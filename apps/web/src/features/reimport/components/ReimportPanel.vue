<script setup lang="ts">
import { computed, ref } from 'vue';

import { useMergeReimportMutation, usePreviewReimportMutation } from '@/features/reimport/composables/useReimport';
import type { ReimportPreview, SectionDiff } from '@/features/reimport/types';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';

const props = defineProps<{
  documentId: string;
  documentVersion: number;
  open: boolean;
}>();

const emit = defineEmits<{
  close: [];
  merged: [];
}>();

const toast = useToast();

const previewMutation = usePreviewReimportMutation();
const mergeMutation = useMergeReimportMutation(computed(() => props.documentId));

// Step tracking
const step = ref<'upload' | 'diff' | 'confirm'>('upload');
const selectedFile = ref<File | null>(null);
const preview = ref<ReimportPreview | null>(null);
const acceptedSections = ref<Set<string>>(new Set());

function handleFileSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files?.length) {
    selectedFile.value = input.files[0];
  }
}

async function previewChanges() {
  if (!selectedFile.value) return;
  try {
    const result = await previewMutation.mutateAsync({
      documentId: props.documentId,
      file: selectedFile.value,
    });
    preview.value = result;
    // Default: accept all modified/new sections
    acceptedSections.value = new Set(
      result.sections
        .filter((s) => s.status === 'modified' || s.status === 'new')
        .map((s) => s.section_name),
    );
    step.value = 'diff';
  } catch (error) {
    toast.error('解析失败', getErrorDescription(error, '请检查文件格式。'));
  }
}

function toggleSection(sectionName: string) {
  const next = new Set(acceptedSections.value);
  if (next.has(sectionName)) {
    next.delete(sectionName);
  } else {
    next.add(sectionName);
  }
  acceptedSections.value = next;
}

const sectionsToAccept = computed(() =>
  preview.value?.sections
    .filter((s) => acceptedSections.value.has(s.section_name))
    .map((s) => s.section_name) ?? [],
);

const sectionsToReject = computed(() =>
  preview.value?.sections
    .filter((s) => !acceptedSections.value.has(s.section_name) && s.status !== 'unchanged')
    .map((s) => s.section_name) ?? [],
);

const modifiedCount = computed(() =>
  preview.value?.sections.filter((s) => s.status !== 'unchanged').length ?? 0,
);

function goToConfirm() {
  step.value = 'confirm';
}

async function confirmMerge() {
  if (!selectedFile.value || !preview.value) return;
  try {
    await mergeMutation.mutateAsync({
      file: selectedFile.value,
      sectionsToAccept: sectionsToAccept.value,
      sectionsToReject: sectionsToReject.value,
      documentVersion: props.documentVersion,
    });
    toast.success(`已合并 ${sectionsToAccept.value.length} 个章节的修改`);
    emit('merged');
    closePanel();
  } catch (error) {
    toast.error('合并失败', getErrorDescription(error));
  }
}

function closePanel() {
  step.value = 'upload';
  selectedFile.value = null;
  preview.value = null;
  acceptedSections.value = new Set();
  emit('close');
}

function renderDiff(diff: SectionDiff): string {
  if (diff.diff_segments) {
    return diff.diff_segments
      .map((seg) => {
        if (seg.type === 'delete') return `[-${seg.text}-]`;
        if (seg.type === 'insert') return `[+${seg.text}+]`;
        return seg.text;
      })
      .join('');
  }
  return '';
}

const statusLabels: Record<string, string> = {
  unchanged: '未修改',
  modified: '已修改',
  new: '新增',
  deleted: '已删除',
};
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="modal-backdrop" @click.self="closePanel">
      <div class="modal-content reimport-modal app-card">
        <div class="modal-header">
          <h3 class="modal-title">导入修改后的 Word</h3>
          <button class="button ghost" type="button" @click="closePanel">✕</button>
        </div>

        <!-- Step 1: Upload -->
        <div v-if="step === 'upload'" class="reimport-step">
          <p class="step-desc">上传在 Word 中修改后保存的 .docx 文件，系统会对比修改内容。</p>
          <label class="file-picker">
            <span>{{ selectedFile ? selectedFile.name : '选择修改后的 Word 文件' }}</span>
            <input type="file" accept=".docx" :disabled="previewMutation.isPending.value" @change="handleFileSelected" />
          </label>
          <button
            v-if="selectedFile"
            class="button primary"
            type="button"
            :disabled="previewMutation.isPending.value"
            @click="previewChanges"
          >
            {{ previewMutation.isPending.value ? '解析中...' : '预览修改' }}
          </button>
        </div>

        <!-- Step 2: Diff display -->
        <div v-if="step === 'diff' && preview" class="reimport-step">
          <p class="step-desc">
            发现 {{ modifiedCount }} 个章节有变动，默认接受全部修改。你可以逐项切换接受/拒绝。
          </p>
          <div class="diff-list">
            <div
              v-for="diff in preview.sections"
              :key="diff.section_name"
              class="diff-item"
              :class="`diff-${diff.status}`"
            >
              <div class="diff-header">
                <span class="diff-title">{{ diff.section_title }}</span>
                <span class="diff-status" :class="diff.status">{{ statusLabels[diff.status] }}</span>
                <label v-if="diff.status !== 'unchanged'" class="diff-toggle">
                  <input
                    type="checkbox"
                    :checked="acceptedSections.has(diff.section_name)"
                    @change="toggleSection(diff.section_name)"
                  />
                  <span>{{ acceptedSections.has(diff.section_name) ? '接受' : '拒绝' }}</span>
                </label>
              </div>

              <!-- Text diff with inline highlighting -->
              <div v-if="diff.diff_segments" class="diff-content text-diff">
                <span
                  v-for="(seg, si) in diff.diff_segments"
                  :key="si"
                  :class="`diff-seg-${seg.type}`"
                >{{ seg.text }}</span>
              </div>

              <!-- Structured diff: side-by-side -->
              <div v-else-if="diff.original_content != null || diff.imported_content != null" class="diff-content side-by-side">
                <div v-if="diff.original_content != null" class="diff-side original">
                  <div class="diff-side-label">当前版本</div>
                  <pre class="diff-pre">{{ typeof diff.original_content === 'string' ? diff.original_content : JSON.stringify(diff.original_content, null, 2) }}</pre>
                </div>
                <div v-if="diff.imported_content != null" class="diff-side imported">
                  <div class="diff-side-label">导入版本</div>
                  <pre class="diff-pre">{{ typeof diff.imported_content === 'string' ? diff.imported_content : JSON.stringify(diff.imported_content, null, 2) }}</pre>
                </div>
              </div>
            </div>
          </div>
          <div class="form-actions">
            <button class="button primary" @click="goToConfirm">继续 →</button>
            <button class="button ghost" @click="step = 'upload'">返回重选</button>
          </div>
        </div>

        <!-- Step 3: Confirm -->
        <div v-if="step === 'confirm'" class="reimport-step">
          <p class="step-desc">确认以下合并操作：</p>
          <ul class="confirm-summary">
            <li v-if="sectionsToAccept.length">
              接受 {{ sectionsToAccept.length }} 个章节的修改
            </li>
            <li v-if="sectionsToReject.length">
              拒绝 {{ sectionsToReject.length }} 个章节的修改，保持当前版本
            </li>
            <li v-if="!sectionsToAccept.length && !sectionsToReject.length">
              没有需要合并的修改
            </li>
          </ul>
          <p class="step-note">合并前会自动保存历史版本，你可以随时回滚。</p>
          <div class="form-actions">
            <button
              class="button primary"
              type="button"
              :disabled="!sectionsToAccept.length || mergeMutation.isPending.value"
              @click="confirmMerge"
            >
              {{ mergeMutation.isPending.value ? '合并中...' : '确认合并' }}
            </button>
            <button class="button ghost" @click="step = 'diff'">返回修改</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
}
.reimport-modal {
  width: 720px;
  max-width: 95vw;
  max-height: 85vh;
  overflow-y: auto;
  padding: 24px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.modal-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
.reimport-step {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.step-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
}
.step-note {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0;
}
.file-picker {
  display: inline-flex;
  padding: 12px 16px;
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
}
.file-picker input { display: none; }

.diff-list {
  max-height: 50vh;
  overflow-y: auto;
}
.diff-item {
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}
.diff-item.diff-modified { border-left: 3px solid var(--color-warning, #f0ad4e); }
.diff-item.diff-new { border-left: 3px solid var(--color-success, #4caf50); }
.diff-item.diff-deleted { border-left: 3px solid var(--color-danger, #f44336); }
.diff-item.diff-unchanged { opacity: 0.6; }
.diff-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.diff-title { font-weight: 600; font-size: 14px; }
.diff-status {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 3px;
}
.diff-status.modified { background: #fff3e0; color: #f0ad4e; }
.diff-status.new { background: #e8f5e9; color: #4caf50; }
.diff-status.deleted { background: #fce4ec; color: #f44336; }
.diff-status.unchanged { background: #f5f5f5; color: #999; }
.diff-toggle {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  cursor: pointer;
}
.diff-content { margin-top: 8px; }
.text-diff {
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  background: var(--color-bg);
  padding: 10px;
  border-radius: 4px;
}
.diff-seg-equal {}
.diff-seg-insert { background: #c8e6c9; }
.diff-seg-delete { background: #ffcdd2; text-decoration: line-through; }

.side-by-side {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.diff-side {
  font-size: 12px;
}
.diff-side-label {
  font-weight: 600;
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.diff-pre {
  background: var(--color-bg);
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
  margin: 0;
}
.original .diff-pre { border-left: 2px solid #f44336; }
.imported .diff-pre { border-left: 2px solid #4caf50; }

.confirm-summary {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.8;
}
.form-actions {
  display: flex;
  gap: 10px;
}
</style>
