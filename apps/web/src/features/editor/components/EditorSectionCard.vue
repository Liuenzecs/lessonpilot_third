<script setup lang="ts">
import type { Block, BlockType, SectionBlock } from '@lessonpilot/shared-types';

import DocumentBlockItem from '@/features/editor/components/DocumentBlockItem.vue';
import EditorSectionSkeleton from '@/features/editor/components/EditorSectionSkeleton.vue';
import PendingBlockCard from '@/features/editor/components/PendingBlockCard.vue';
import type { InsertableBlockType } from '@/shared/utils/content';

defineProps<{
  section: SectionBlock;
  activeBlockId: string | null;
  openMenuBlockId: string | null;
  loadingTargetId: string | null;
  showSkeleton: boolean;
  isCurrentGenerating: boolean;
}>();

defineEmits<{
  activate: [blockId: string];
  'update:block': [block: Block];
  'toggle-menu': [blockId: string | null];
  move: [payload: { blockId: string; direction: 'up' | 'down' }];
  delete: [blockId: string];
  convert: [payload: { blockId: string; targetType: BlockType }];
  rewrite: [payload: { blockId: string; action: 'rewrite' }];
  reorder: [payload: { draggedId: string; targetId: string; parentId: string }];
  'add-child': [payload: { parentId: string; type: InsertableBlockType }];
  'selection-rewrite': [payload: { blockId: string; action: 'polish' | 'expand'; selectionText: string }];
  'accept-pending': [blockId: string];
  'reject-pending': [blockId: string];
  'regenerate-pending': [payload: { targetBlockId: string; action: 'rewrite' | 'polish' | 'expand' }];
  'regenerate-section': [sectionId: string];
}>();

function getSectionConfirmedChildren(section: SectionBlock): Block[] {
  return section.children.filter((child) => child.status === 'confirmed');
}

function getSectionAppendPending(section: SectionBlock): Block[] {
  return section.children.filter(
    (child) => child.status === 'pending' && child.suggestion?.kind !== 'replace',
  );
}

function getSectionTargetedPending(section: SectionBlock, targetBlockId: string): Block[] {
  return section.children.filter(
    (child) =>
      child.status === 'pending' &&
      child.suggestion?.kind === 'replace' &&
      child.suggestion.targetBlockId === targetBlockId,
  );
}
</script>

<template>
  <section class="section-card">
    <div class="editor-toolbar">
      <div>
        <h2 style="margin: 0">{{ section.title }}</h2>
        <div class="task-meta">
          {{ getSectionConfirmedChildren(section).length }} 个已确认 Block，
          {{ section.children.filter((child) => child.status === 'pending').length }} 个待确认 Block
        </div>
      </div>
      <div class="section-actions">
        <button class="button ghost" type="button" @click="$emit('add-child', { parentId: section.id, type: 'paragraph' })">
          添加段落
        </button>
        <button class="button ghost" type="button" @click="$emit('add-child', { parentId: section.id, type: 'list' })">
          添加列表
        </button>
        <button class="button ghost" type="button" @click="$emit('add-child', { parentId: section.id, type: 'teaching_step' })">
          添加教学步骤
        </button>
        <button class="button ghost" type="button" @click="$emit('add-child', { parentId: section.id, type: 'exercise_group' })">
          添加题组
        </button>
        <button class="button secondary" type="button" @click="$emit('regenerate-section', section.id)">
          AI 重新生成本节
        </button>
      </div>
    </div>

    <EditorSectionSkeleton v-if="showSkeleton && section.children.length === 0" :title="section.title" :is-current="isCurrentGenerating" />

    <template v-else>
      <DocumentBlockItem
        v-for="child in getSectionConfirmedChildren(section)"
        :key="child.id"
        :block="child"
        :parent-id="section.id"
        :active-block-id="activeBlockId"
        :open-menu-block-id="openMenuBlockId"
        :loading-target-id="loadingTargetId"
        :pending-suggestions="getSectionTargetedPending(section, child.id)"
        @activate="$emit('activate', $event)"
        @update:block="$emit('update:block', $event)"
        @toggle-menu="$emit('toggle-menu', $event)"
        @move="$emit('move', $event)"
        @delete="$emit('delete', $event)"
        @convert="$emit('convert', $event)"
        @rewrite="$emit('rewrite', $event)"
        @reorder="$emit('reorder', $event)"
        @add-child="$emit('add-child', $event)"
        @selection-rewrite="$emit('selection-rewrite', $event)"
        @accept-pending="$emit('accept-pending', $event)"
        @reject-pending="$emit('reject-pending', $event)"
        @regenerate-pending="$emit('regenerate-pending', $event)"
      />

      <PendingBlockCard
        v-for="pendingBlock in getSectionAppendPending(section)"
        :key="pendingBlock.id"
        :block="pendingBlock"
        @accept="$emit('accept-pending', pendingBlock.id)"
        @reject="$emit('reject-pending', pendingBlock.id)"
      />

      <div v-if="getSectionConfirmedChildren(section).length === 0 && section.children.length === 0" class="muted">
        这一节还没有内容，你可以手动补充，或者使用 AI 生成。
      </div>
    </template>
  </section>
</template>
