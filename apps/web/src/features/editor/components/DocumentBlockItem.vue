<script setup lang="ts">
import type { Block, BlockType } from '@lessonpilot/shared-types';

import { computed } from 'vue';

import BlockRenderer from '@/features/editor/components/BlockRenderer.vue';
import PendingBlockCard from '@/features/editor/components/PendingBlockCard.vue';
import type { InsertableBlockType } from '@/shared/utils/content';

defineOptions({
  name: 'DocumentBlockItem',
});

const props = defineProps<{
  block: Block;
  parentId: string;
  activeBlockId: string | null;
  openMenuBlockId: string | null;
  loadingTargetId: string | null;
  pendingSuggestions?: Block[];
}>();

const emit = defineEmits<{
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
}>();

const isActive = computed(() => props.activeBlockId === props.block.id);
const menuOpen = computed(() => props.openMenuBlockId === props.block.id);
const isContainer = computed(() =>
  ['teaching_step', 'exercise_group'].includes(props.block.type),
);

const appendChildren = computed(() => {
  if (!isContainer.value || !('children' in props.block)) {
    return [];
  }
  return props.block.children.filter(
    (child) => child.status === 'pending' && child.suggestion?.kind !== 'replace',
  );
});

const confirmedChildren = computed(() => {
  if (!isContainer.value || !('children' in props.block)) {
    return [];
  }
  return props.block.children.filter((child) => child.status === 'confirmed');
});

function getTargetedPendingSuggestions(targetBlockId: string): Block[] {
  if (!isContainer.value || !('children' in props.block)) {
    return [];
  }
  return props.block.children.filter(
    (child) =>
      child.status === 'pending' &&
      child.suggestion?.kind === 'replace' &&
      child.suggestion.targetBlockId === targetBlockId,
  );
}

function getChildActions(blockType: BlockType): Array<{ type: InsertableBlockType; label: string }> {
  if (blockType === 'teaching_step') {
    return [
      { type: 'paragraph', label: '添加段落' },
      { type: 'list', label: '添加列表' },
    ];
  }
  if (blockType === 'exercise_group') {
    return [
      { type: 'choice_question', label: '添加选择题' },
      { type: 'fill_blank_question', label: '添加填空题' },
      { type: 'short_answer_question', label: '添加简答题' },
    ];
  }
  return [];
}

function getConvertTargets(blockType: BlockType): BlockType[] {
  if (blockType === 'paragraph') {
    return ['list'];
  }
  if (blockType === 'list') {
    return ['paragraph'];
  }
  if (blockType === 'choice_question') {
    return ['fill_blank_question', 'short_answer_question'];
  }
  if (blockType === 'fill_blank_question') {
    return ['choice_question', 'short_answer_question'];
  }
  if (blockType === 'short_answer_question') {
    return ['choice_question', 'fill_blank_question'];
  }
  return [];
}

function getBlockLabel(blockType: BlockType): string {
  const labels: Record<BlockType, string> = {
    section: '章节',
    paragraph: '段落',
    list: '列表',
    teaching_step: '教学步骤',
    exercise_group: '题组',
    choice_question: '选择题',
    fill_blank_question: '填空题',
    short_answer_question: '简答题',
  };

  return labels[blockType];
}

function onDragStart(event: DragEvent) {
  event.dataTransfer?.setData(
    'application/lessonpilot-block',
    JSON.stringify({ blockId: props.block.id, parentId: props.parentId }),
  );
  event.dataTransfer?.setData('text/plain', props.block.id);
  event.dataTransfer!.effectAllowed = 'move';
}

function onDrop(event: DragEvent) {
  const raw = event.dataTransfer?.getData('application/lessonpilot-block');
  if (!raw) {
    return;
  }

  try {
    const payload = JSON.parse(raw) as { blockId: string; parentId: string };
    if (payload.parentId !== props.parentId || payload.blockId === props.block.id) {
      return;
    }
    emit('reorder', {
      draggedId: payload.blockId,
      targetId: props.block.id,
      parentId: props.parentId,
    });
  } catch {
    // Ignore invalid drag payloads.
  }
}

function canRegenerate(block: Block): boolean {
  return Boolean(block.suggestion?.targetBlockId && block.suggestion.action);
}

function updateContainerChild(nextChild: Block) {
  if (!('children' in props.block)) {
    return;
  }
  emit('update:block', {
    ...props.block,
    children: props.block.children.map((currentChild) =>
      currentChild.id === nextChild.id ? nextChild : currentChild,
    ),
  } as Block);
}
</script>

<template>
  <div
    class="editable-block-shell"
    :class="{ active: isActive }"
    @click.stop="emit('activate', block.id)"
    @focusin="emit('activate', block.id)"
    @dragover.prevent
    @drop.stop="onDrop"
  >
    <div class="block-handle-column">
      <button class="drag-handle" type="button" draggable="true" @dragstart="onDragStart">⋮⋮</button>
    </div>

    <div class="block-shell-main">
      <div class="block-shell-header">
        <div class="block-kind">{{ getBlockLabel(block.type) }}</div>
        <div class="block-shell-actions" :class="{ 'menu-open': menuOpen }">
          <button class="icon-button" type="button" @click.stop="emit('toggle-menu', menuOpen ? null : block.id)">
            ⋯
          </button>
          <div v-if="menuOpen" class="block-menu">
            <button class="menu-button" type="button" @click="emit('rewrite', { blockId: block.id, action: 'rewrite' })">
              AI 重写
            </button>
            <button class="menu-button" type="button" @click="emit('move', { blockId: block.id, direction: 'up' })">
              上移
            </button>
            <button class="menu-button" type="button" @click="emit('move', { blockId: block.id, direction: 'down' })">
              下移
            </button>
            <button
              v-for="targetType in getConvertTargets(block.type)"
              :key="`${block.id}-${targetType}`"
              class="menu-button"
              type="button"
              @click="emit('convert', { blockId: block.id, targetType })"
            >
              转为 {{ targetType.replaceAll('_', ' ') }}
            </button>
            <button class="menu-button danger" type="button" @click="emit('delete', block.id)">删除</button>
          </div>
        </div>
      </div>

      <BlockRenderer
        :block="block"
        @update:block="emit('update:block', $event)"
        @selection-action="emit('selection-rewrite', { blockId: block.id, ...$event })"
      />

      <div v-if="loadingTargetId === block.id" class="pending-skeleton-card">
        AI 正在重写这段内容...
      </div>

      <PendingBlockCard
        v-for="pendingBlock in pendingSuggestions || []"
        :key="pendingBlock.id"
        :block="pendingBlock"
        label="AI 替换建议"
        :can-regenerate="canRegenerate(pendingBlock)"
        @accept="emit('accept-pending', pendingBlock.id)"
        @reject="emit('reject-pending', pendingBlock.id)"
        @regenerate="
          emit('regenerate-pending', {
            targetBlockId: pendingBlock.suggestion!.targetBlockId!,
            action: pendingBlock.suggestion!.action!,
          })
        "
      />

      <div v-if="isContainer" class="nested-blocks">
        <div class="nested-toolbar">
          <button
            v-for="action in getChildActions(block.type)"
            :key="`${block.id}-${action.type}`"
            class="button secondary"
            type="button"
            @click="emit('add-child', { parentId: block.id, type: action.type })"
          >
            {{ action.label }}
          </button>
        </div>

        <DocumentBlockItem
          v-for="child in confirmedChildren"
          :key="child.id"
          :block="child"
          :parent-id="block.id"
          :active-block-id="activeBlockId"
          :open-menu-block-id="openMenuBlockId"
          :loading-target-id="loadingTargetId"
          :pending-suggestions="getTargetedPendingSuggestions(child.id)"
          @activate="emit('activate', $event)"
          @update:block="updateContainerChild"
          @toggle-menu="emit('toggle-menu', $event)"
          @move="emit('move', $event)"
          @delete="emit('delete', $event)"
          @convert="emit('convert', $event)"
          @rewrite="emit('rewrite', $event)"
          @reorder="emit('reorder', $event)"
          @add-child="emit('add-child', $event)"
          @selection-rewrite="emit('selection-rewrite', $event)"
          @accept-pending="emit('accept-pending', $event)"
          @reject-pending="emit('reject-pending', $event)"
          @regenerate-pending="emit('regenerate-pending', $event)"
        />

        <PendingBlockCard
          v-for="pendingBlock in appendChildren"
          :key="pendingBlock.id"
          :block="pendingBlock"
          @accept="emit('accept-pending', pendingBlock.id)"
          @reject="emit('reject-pending', pendingBlock.id)"
        />
      </div>
    </div>
  </div>
</template>
