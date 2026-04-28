<script setup lang="ts">
/** 班级组管理页 — 创建/编辑/删除班级组，用于同课多班差异化。 */
import { ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  useClassGroups,
  useCreateClassGroupMutation,
  useDeleteClassGroupMutation,
  useUpdateClassGroupMutation,
} from '@/features/task/composables/useClassGroups';
import StatePanel from '@/shared/components/StatePanel.vue';
import { useToast } from '@/shared/composables/useToast';

const router = useRouter();
const toast = useToast();

const { data: classGroups, isLoading } = useClassGroups();
const createMutation = useCreateClassGroupMutation();
const updateMutation = useUpdateClassGroupMutation();
const deleteMutation = useDeleteClassGroupMutation();

const showCreateForm = ref(false);
const editingId = ref<string | null>(null);

const newName = ref('');
const newLevel = ref('standard');
const newNotes = ref('');

const editName = ref('');
const editLevel = ref('standard');
const editNotes = ref('');

const levelLabels: Record<string, string> = {
  standard: '普通班',
  advanced: '重点班',
  remedial: '基础班',
};

function resetCreateForm() {
  newName.value = '';
  newLevel.value = 'standard';
  newNotes.value = '';
  showCreateForm.value = false;
}

async function handleCreate() {
  if (!newName.value.trim()) return;
  try {
    await createMutation.mutateAsync({
      name: newName.value.trim(),
      level: newLevel.value,
      notes: newNotes.value.trim() || null,
    });
    toast.success('班级组已创建');
    resetCreateForm();
  } catch {
    toast.error('创建失败', '请稍后重试。');
  }
}

function startEdit(cg: { id: string; name: string; level: string; notes: string | null }) {
  editingId.value = cg.id;
  editName.value = cg.name;
  editLevel.value = cg.level;
  editNotes.value = cg.notes ?? '';
}

function cancelEdit() {
  editingId.value = null;
}

async function handleUpdate(id: string) {
  if (!editName.value.trim()) return;
  try {
    await updateMutation.mutateAsync({
      id,
      name: editName.value.trim(),
      level: editLevel.value,
      notes: editNotes.value.trim() || null,
    });
    toast.success('班级组已更新');
    cancelEdit();
  } catch {
    toast.error('更新失败', '请稍后重试。');
  }
}

async function handleDelete(id: string) {
  try {
    await deleteMutation.mutateAsync(id);
    toast.success('班级组已删除');
  } catch {
    toast.error('删除失败', '请稍后重试。');
  }
}
</script>

<template>
  <div class="page-shell">
    <div class="page-head">
      <div>
        <h1>班级管理</h1>
        <p class="page-subtitle">管理你的班级分组，同一课题可为不同班级生成差异化版本。</p>
      </div>
      <div class="page-head-actions">
        <button class="button ghost" type="button" @click="router.back()">返回</button>
        <button class="button primary" type="button" @click="showCreateForm = true">新建班级组</button>
      </div>
    </div>

    <StatePanel
      v-if="isLoading"
      icon="📋"
      eyebrow="班级管理"
      title="正在加载..."
      tone="info"
    />

    <div v-else class="class-group-list">
      <div v-if="!classGroups?.length && !showCreateForm" class="workspace-empty-state">
        <div class="workspace-empty-icon">🏫</div>
        <h2>还没有班级组</h2>
        <p>创建班级组后，你可以为不同班级生成同一课题的差异化备课版本。</p>
        <button class="button primary" type="button" @click="showCreateForm = true">新建班级组</button>
      </div>

      <!-- Create form -->
      <div v-if="showCreateForm" class="class-group-card">
        <div class="class-group-form">
          <input
            v-model="newName"
            class="create-input"
            placeholder="班级名称，如：高一3班"
            @keyup.enter="handleCreate"
          />
          <select v-model="newLevel" class="create-input">
            <option value="standard">普通班</option>
            <option value="advanced">重点班</option>
            <option value="remedial">基础班</option>
          </select>
          <input v-model="newNotes" class="create-input" placeholder="备注（可选）" />
          <div class="class-group-actions">
            <button class="button primary" type="button" :disabled="createMutation.isPending.value" @click="handleCreate">
              {{ createMutation.isPending.value ? '创建中...' : '确认创建' }}
            </button>
            <button class="button ghost" type="button" @click="resetCreateForm">取消</button>
          </div>
        </div>
      </div>

      <!-- List -->
      <div
        v-for="cg in (classGroups ?? [])"
        :key="cg.id"
        class="class-group-card"
      >
        <div v-if="editingId !== cg.id" class="class-group-row">
          <div class="class-group-info">
            <div class="class-group-name">
              {{ cg.name }}
              <span class="class-group-level" :class="`level-${cg.level}`">
                {{ levelLabels[cg.level] ?? cg.level }}
              </span>
            </div>
            <p v-if="cg.notes" class="class-group-notes">{{ cg.notes }}</p>
          </div>
          <div class="class-group-row-actions">
            <button class="button ghost" type="button" @click="startEdit(cg)">编辑</button>
            <button class="button ghost danger" type="button" @click="handleDelete(cg.id)">删除</button>
          </div>
        </div>
        <div v-else class="class-group-form">
          <input v-model="editName" class="create-input" placeholder="班级名称" />
          <select v-model="editLevel" class="create-input">
            <option value="standard">普通班</option>
            <option value="advanced">重点班</option>
            <option value="remedial">基础班</option>
          </select>
          <input v-model="editNotes" class="create-input" placeholder="备注（可选）" />
          <div class="class-group-actions">
            <button class="button primary" type="button" :disabled="updateMutation.isPending.value" @click="handleUpdate(cg.id)">
              {{ updateMutation.isPending.value ? '保存中...' : '保存' }}
            </button>
            <button class="button ghost" type="button" @click="cancelEdit">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.page-head h1 {
  margin: 0 0 4px;
  font-size: 24px;
}

.page-subtitle {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.page-head-actions {
  display: flex;
  gap: 8px;
}

.class-group-list {
  display: grid;
  gap: 10px;
}

.class-group-card {
  padding: 16px 18px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
}

.class-group-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.class-group-info {
  min-width: 0;
}

.class-group-name {
  font-size: 16px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.class-group-level {
  padding: 2px 8px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 800;
}

.class-group-level.level-standard {
  background: rgba(var(--primary-rgb), 0.08);
  color: var(--primary);
}
.class-group-level.level-advanced {
  background: rgba(var(--success-rgb), 0.08);
  color: var(--success);
}
.class-group-level.level-remedial {
  background: rgba(var(--warning-rgb), 0.1);
  color: var(--warning);
}

.class-group-notes {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 13px;
}

.class-group-row-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.class-group-form {
  display: grid;
  gap: 10px;
}

.class-group-form .create-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-micro);
  background: var(--surface);
  color: var(--text);
  font-size: 14px;
}

.class-group-actions {
  display: flex;
  gap: 8px;
}

.danger {
  color: var(--danger);
}

@media (max-width: 600px) {
  .page-head {
    flex-direction: column;
  }
  .class-group-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .class-group-row-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
