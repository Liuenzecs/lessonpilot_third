<script setup lang="ts">
import type {
  Block,
  ChoiceQuestionBlock,
  FillBlankQuestionBlock,
  ListBlock,
  ParagraphBlock,
  ShortAnswerQuestionBlock,
  TeachingStepBlock,
  ExerciseGroupBlock,
} from '@lessonpilot/shared-types';

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
  'selection-action': [payload: { action: 'polish' | 'expand'; selectionText: string }];
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

function updateExerciseGroup(partial: Partial<ExerciseGroupBlock>) {
  if (props.block.type !== 'exercise_group') {
    return;
  }
  emitBlock({
    ...props.block,
    ...partial,
  } satisfies ExerciseGroupBlock);
}

function updateChoiceQuestion(partial: Partial<ChoiceQuestionBlock>) {
  if (props.block.type !== 'choice_question') {
    return;
  }
  emitBlock({
    ...props.block,
    ...partial,
  } satisfies ChoiceQuestionBlock);
}

function updateFillBlankQuestion(partial: Partial<FillBlankQuestionBlock>) {
  if (props.block.type !== 'fill_blank_question') {
    return;
  }
  emitBlock({
    ...props.block,
    ...partial,
  } satisfies FillBlankQuestionBlock);
}

function updateShortAnswerQuestion(partial: Partial<ShortAnswerQuestionBlock>) {
  if (props.block.type !== 'short_answer_question') {
    return;
  }
  emitBlock({
    ...props.block,
    ...partial,
  } satisfies ShortAnswerQuestionBlock);
}

function updateArrayValue<T>(values: T[], index: number, nextValue: T): T[] {
  const nextValues = [...values];
  nextValues[index] = nextValue;
  return nextValues;
}
</script>

<template>
  <div class="block-content">
    <template v-if="block.type === 'paragraph'">
      <RichTextField
        :model-value="block.content"
        :disabled="readonly"
        allow-selection-ai
        @update:model-value="updateParagraph"
        @selection-action="$emit('selection-action', $event)"
      />
    </template>

    <template v-else-if="block.type === 'list'">
      <div class="list-editor">
        <div v-for="(item, index) in block.items" :key="`${block.id}-${index}`" class="list-item">
          <span>•</span>
          <template v-if="readonly">
            <div>{{ item }}</div>
          </template>
          <template v-else>
            <input :value="item" type="text" @input="updateListItem(index, ($event.target as HTMLInputElement).value)" />
            <button class="button ghost" type="button" @click="removeListItem(index)">删除</button>
          </template>
        </div>
        <button v-if="!readonly" class="button secondary" type="button" @click="addListItem">添加条目</button>
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
    </template>

    <template v-else-if="block.type === 'exercise_group'">
      <div class="field">
        <label>题组标题</label>
        <input
          :disabled="readonly"
          :value="block.title"
          type="text"
          @input="updateExerciseGroup({ title: ($event.target as HTMLInputElement).value })"
        />
      </div>
    </template>

    <template v-else-if="block.type === 'choice_question'">
      <div class="field">
        <label>题干</label>
        <RichTextField :model-value="block.prompt" :disabled="readonly" @update:model-value="updateChoiceQuestion({ prompt: $event })" />
      </div>
      <div class="field">
        <label>选项</label>
        <div class="stacked-fields">
          <div v-for="(option, index) in block.options" :key="`${block.id}-option-${index}`" class="inline-input-row">
            <input
              :disabled="readonly"
              :value="option"
              type="text"
              @input="
                updateChoiceQuestion({
                  options: updateArrayValue(block.options, index, ($event.target as HTMLInputElement).value),
                })
              "
            />
          </div>
        </div>
      </div>
      <div class="field">
        <label>答案（每行一个）</label>
        <textarea
          :disabled="readonly"
          :value="block.answers.join('\n')"
          rows="3"
          @input="
            updateChoiceQuestion({
              answers: ($event.target as HTMLTextAreaElement).value
                .split('\n')
                .map((item) => item.trim())
                .filter(Boolean),
            })
          "
        />
      </div>
      <div class="field">
        <label>解析</label>
        <RichTextField
          :model-value="block.analysis"
          :disabled="readonly"
          @update:model-value="updateChoiceQuestion({ analysis: $event })"
        />
      </div>
    </template>

    <template v-else-if="block.type === 'fill_blank_question'">
      <div class="field">
        <label>题干</label>
        <RichTextField
          :model-value="block.prompt"
          :disabled="readonly"
          @update:model-value="updateFillBlankQuestion({ prompt: $event })"
        />
      </div>
      <div class="field">
        <label>答案（每行一个）</label>
        <textarea
          :disabled="readonly"
          :value="block.answers.join('\n')"
          rows="3"
          @input="
            updateFillBlankQuestion({
              answers: ($event.target as HTMLTextAreaElement).value
                .split('\n')
                .map((item) => item.trim())
                .filter(Boolean),
            })
          "
        />
      </div>
      <div class="field">
        <label>解析</label>
        <RichTextField
          :model-value="block.analysis"
          :disabled="readonly"
          @update:model-value="updateFillBlankQuestion({ analysis: $event })"
        />
      </div>
    </template>

    <template v-else-if="block.type === 'short_answer_question'">
      <div class="field">
        <label>题干</label>
        <RichTextField
          :model-value="block.prompt"
          :disabled="readonly"
          @update:model-value="updateShortAnswerQuestion({ prompt: $event })"
        />
      </div>
      <div class="field">
        <label>参考答案</label>
        <RichTextField
          :model-value="block.referenceAnswer"
          :disabled="readonly"
          @update:model-value="updateShortAnswerQuestion({ referenceAnswer: $event })"
        />
      </div>
      <div class="field">
        <label>解析</label>
        <RichTextField
          :model-value="block.analysis"
          :disabled="readonly"
          @update:model-value="updateShortAnswerQuestion({ analysis: $event })"
        />
      </div>
    </template>
  </div>
</template>
