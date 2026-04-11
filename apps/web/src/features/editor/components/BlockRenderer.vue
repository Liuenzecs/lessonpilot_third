<script setup lang="ts">
import type { Block, ListBlock, ParagraphBlock, TeachingStepBlock } from '@lessonpilot/shared-types';

import RichTextField from '@/features/editor/components/RichTextField.vue';

const props = withDefaults(
  defineProps<{
    block: Block;
    readonly?: boolean;
  }>(),
  {
    readonly: false,
  },
);

const emit = defineEmits<{
  'update:block': [block: Block];
}>();

function emitBlock(nextBlock: Block) {
  emit('update:block', nextBlock);
}

function updateParagraph(content: string) {
  emitBlock({
    ...(props.block as ParagraphBlock),
    content,
  });
}

function updateListItem(index: number, value: string) {
  if (props.block.type !== 'list') {
    return;
  }

  const items = [...props.block.items];
  items[index] = value;
  emitBlock({
    ...props.block,
    items,
  } satisfies ListBlock);
}

function addListItem() {
  if (props.block.type !== 'list') {
    return;
  }

  emitBlock({
    ...props.block,
    items: [...props.block.items, ''],
  } satisfies ListBlock);
}

function removeListItem(index: number) {
  if (props.block.type !== 'list') {
    return;
  }

  emitBlock({
    ...props.block,
    items: props.block.items.filter((_, itemIndex) => itemIndex !== index),
  } satisfies ListBlock);
}

function updateTeachingStep(partial: Partial<TeachingStepBlock>) {
  if (props.block.type !== 'teaching_step') {
    return;
  }

  emitBlock({
    ...props.block,
    ...partial,
  } satisfies TeachingStepBlock);
}

function updateTeachingStepChild(index: number, child: Block) {
  if (props.block.type !== 'teaching_step') {
    return;
  }

  const children = props.block.children.map((currentChild, currentIndex) =>
    currentIndex === index ? child : currentChild,
  );
  updateTeachingStep({ children });
}

function addParagraphChild() {
  if (props.block.type !== 'teaching_step') {
    return;
  }

  updateTeachingStep({
    children: [
      ...props.block.children,
      {
        id: crypto.randomUUID(),
        type: 'paragraph',
        content: '<p></p>',
        status: 'confirmed',
        source: 'human',
      },
    ],
  });
}

function addListChild() {
  if (props.block.type !== 'teaching_step') {
    return;
  }

  updateTeachingStep({
    children: [
      ...props.block.children,
      {
        id: crypto.randomUUID(),
        type: 'list',
        items: [''],
        status: 'confirmed',
        source: 'human',
      },
    ],
  });
}
</script>

<template>
  <div class="block-card">
    <template v-if="block.type === 'paragraph'">
      <RichTextField
        :model-value="block.content"
        :disabled="readonly"
        @update:model-value="updateParagraph"
      />
    </template>

    <template v-else-if="block.type === 'list'">
      <div class="list-editor">
        <div
          v-for="(item, index) in block.items"
          :key="`${block.id}-${index}`"
          class="list-item"
        >
          <span>•</span>
          <template v-if="readonly">
            <div>{{ item }}</div>
          </template>
          <template v-else>
            <input
              :value="item"
              type="text"
              @input="updateListItem(index, ($event.target as HTMLInputElement).value)"
            />
            <button class="button ghost" type="button" @click="removeListItem(index)">
              删除
            </button>
          </template>
        </div>
        <button
          v-if="!readonly"
          class="button secondary"
          type="button"
          @click="addListItem"
        >
          添加条目
        </button>
      </div>
    </template>

    <template v-else-if="block.type === 'teaching_step'">
      <div class="field">
        <label>教学步骤标题</label>
        <input
          :disabled="readonly"
          :value="block.title"
          type="text"
          @input="updateTeachingStep({ title: ($event.target as HTMLInputElement).value })"
        />
      </div>
      <div class="field">
        <label>时长（分钟）</label>
        <input
          :disabled="readonly"
          :value="block.durationMinutes ?? ''"
          min="0"
          type="number"
          @input="
            updateTeachingStep({
              durationMinutes: Number(($event.target as HTMLInputElement).value) || null,
            })
          "
        />
      </div>
      <div class="block-actions" v-if="!readonly">
        <button class="button secondary" type="button" @click="addParagraphChild">
          添加段落
        </button>
        <button class="button secondary" type="button" @click="addListChild">
          添加列表
        </button>
      </div>
      <BlockRenderer
        v-for="(child, index) in block.children"
        :key="child.id"
        :block="child"
        :readonly="readonly"
        @update:block="updateTeachingStepChild(index, $event)"
      />
    </template>
  </div>
</template>

