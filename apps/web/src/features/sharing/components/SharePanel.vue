<script setup lang="ts">
import { computed, ref, toRef } from 'vue';

import { useCreateShareLinkMutation, useDeleteShareLinkMutation, useShareLinks, useUpdateShareLinkMutation } from '@/features/sharing/composables/useSharing';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';

const props = defineProps<{
  documentId: string | null;
  open: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const toast = useToast();
const docId = toRef(props, 'documentId');
const shareQueryEnabled = computed(() => props.open && Boolean(props.documentId));

const { data: shareLinks, isLoading } = useShareLinks(
  docId as unknown as import('vue').Ref<string | null>,
  shareQueryEnabled,
);

const createMutation = useCreateShareLinkMutation(docId as unknown as import('vue').Ref<string>);
const updateMutation = useUpdateShareLinkMutation(docId as unknown as import('vue').Ref<string>);
const deleteMutation = useDeleteShareLinkMutation(docId as unknown as import('vue').Ref<string>);

const permission = ref<'read' | 'comment'>('read');
const expiresInDays = ref<number | null>(null);

async function handleCreate() {
  try {
    await createMutation.mutateAsync({
      permission: permission.value,
      expires_in_days: expiresInDays.value ?? undefined,
    });
    toast.success('分享链接已生成');
  } catch (error) {
    toast.error('生成失败', getErrorDescription(error));
  }
}

async function handleToggle(shareId: string, currentActive: boolean) {
  try {
    await updateMutation.mutateAsync({
      shareId,
      payload: { is_active: !currentActive },
    });
  } catch (error) {
    toast.error('操作失败', getErrorDescription(error));
  }
}

async function handleDelete(shareId: string) {
  try {
    await deleteMutation.mutateAsync(shareId);
    toast.success('分享链接已停用');
  } catch (error) {
    toast.error('删除失败', getErrorDescription(error));
  }
}

function copyUrl(url: string) {
  void navigator.clipboard.writeText(url);
  toast.success('链接已复制到剪贴板');
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="drawer-backdrop" @click.self="$emit('close')">
      <aside class="drawer share-panel app-card">
        <div class="share-panel-header">
          <h3 class="share-panel-title">分享文档</h3>
          <button class="button ghost" type="button" @click="$emit('close')">✕</button>
        </div>

        <!-- Create form -->
        <div class="share-create">
          <div class="share-create-row">
            <label class="share-label">权限</label>
            <select v-model="permission" class="input">
              <option value="read">只读</option>
              <option value="comment">可评论</option>
            </select>
          </div>
          <div class="share-create-row">
            <label class="share-label">过期时间</label>
            <select v-model="expiresInDays" class="input">
              <option :value="null">永不过期</option>
              <option :value="7">7 天</option>
              <option :value="30">30 天</option>
              <option :value="90">90 天</option>
            </select>
          </div>
          <button
            class="button primary"
            type="button"
            :disabled="createMutation.isPending.value"
            @click="handleCreate"
          >
            {{ createMutation.isPending.value ? '生成中...' : '生成分享链接' }}
          </button>
        </div>

        <!-- Existing links -->
        <div v-if="isLoading" class="share-loading">加载中...</div>
        <div v-else-if="shareLinks?.length" class="share-links">
          <h4 class="share-links-title">已有链接</h4>
          <div v-for="link in shareLinks" :key="link.id" class="share-link-item">
            <div class="share-link-info">
              <span class="share-link-permission" :class="link.permission">
                {{ link.permission === 'comment' ? '可评论' : '只读' }}
              </span>
              <span v-if="!link.is_active" class="badge inactive">已停用</span>
              <span v-if="link.expires_at" class="share-link-expiry">
                过期: {{ new Date(link.expires_at).toLocaleDateString() }}
              </span>
            </div>
            <div class="share-link-url">{{ link.url }}</div>
            <div class="share-link-actions">
              <button class="button ghost small" type="button" @click="copyUrl(link.url)">复制</button>
              <button class="button ghost small" type="button" @click="handleToggle(link.id, link.is_active)">
                {{ link.is_active ? '停用' : '启用' }}
              </button>
              <button class="button ghost danger small" type="button" @click="handleDelete(link.id)">删除</button>
            </div>
          </div>
        </div>
        <p v-else class="share-empty">暂无分享链接，点击上方按钮生成。</p>
      </aside>
    </div>
  </Teleport>
</template>

<style scoped>
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 100;
  display: flex;
  justify-content: flex-end;
}
.share-panel {
  width: 420px;
  max-width: 90vw;
  height: 100%;
  overflow-y: auto;
  padding: 24px;
  border-radius: 0;
}
.share-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.share-panel-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
.share-create {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border);
}
.share-create-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.share-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}
.share-links-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px;
}
.share-link-item {
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
}
.share-link-info {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
  font-size: 12px;
}
.share-link-permission {
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 11px;
  background: var(--color-primary-light, #e8f4f8);
  color: var(--color-primary);
}
.share-link-permission.comment {
  background: var(--color-success-light, #e8f5e9);
  color: var(--color-success);
}
.badge.inactive {
  background: var(--color-bg-muted);
  color: var(--color-text-secondary);
}
.share-link-expiry {
  color: var(--color-text-secondary);
}
.share-link-url {
  font-size: 12px;
  color: var(--color-text-secondary);
  word-break: break-all;
  margin-bottom: 8px;
}
.share-link-actions {
  display: flex;
  gap: 6px;
}
.button.small {
  font-size: 12px;
  padding: 4px 8px;
}
.share-empty, .share-loading {
  font-size: 13px;
  color: var(--color-text-secondary);
  text-align: center;
  padding: 20px 0;
}
</style>
