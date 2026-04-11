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
  'insert-paragraph-after': [blockId: string];
  'indent-block': [payload: { blockId: string; direction: 'in' | 'out' }];
  'list-insert-item': [payload: { blockId: string; index: number }];
  'list-exit-to-paragraph': [payload: { blockId: string; index: number }];
  'accept-pending': [blockId: string];
  'reject-pending': [blockId: string];
  'regenerate-pending': [payload: {
    targetBlockId: string;
    action: 'rewrite' | 'polish' | 'expand';
    mode: 'block' | 'selection';
    selectionText?: string;
  }];
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
    <div class="section-card-head">
      <div class="section-card-title-group">
        <h2 class="section-card-title">{{ section.title }}</h2>
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

    <EditorSectionSkeleton
      v-if="showSkeleton && section.children.length === 0"
      :title="section.title"
      :is-current="isCurrentGenerating"
    />

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
        @insert-paragraph-after="$emit('insert-paragraph-after', $event)"
        @indent-block="$emit('indent-block', $event)"
        @list-insert-item="$emit('list-insert-item', $event)"
        @list-exit-to-paragraph="$emit('list-exit-to-paragraph', $event)"
        @accept-pending="$emit('accept-pending', $event)"
        @reject-pending="$emit('reject-pending', $event)"
        @regenerate-pending="$emit('regenerate-pending', $event)"
      />

      <PendingBlockCard
        v-for="pendingBlock in getSectionAppendPending(section)"
        :key="pendingBlock.id"
        :block="pendingBlock"
        label="AI 待确认"
        @accept="$emit('accept-pending', pendingBlock.id)"
        @reject="$emit('reject-pending', pendingBlock.id)"
      />

      <div v-if="getSectionConfirmedChildren(section).length === 0 && section.children.length === 0" class="section-empty">
        这一节还没有内容。你可以先手动添加段落，也可以使用 AI 重新生成本节。
      </div>
    </template>
  </section>
</template>
