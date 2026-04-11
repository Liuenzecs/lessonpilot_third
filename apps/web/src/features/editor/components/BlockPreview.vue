<script setup lang="ts">
import type { Block } from '@lessonpilot/shared-types';

import { isContainerBlock } from '@lessonpilot/shared-types';

defineOptions({
  name: 'BlockPreview',
});

defineProps<{
  block: Block;
}>();

function toText(value: string): string {
  return value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function renderAnswers(value: string[] | string): string {
  return Array.isArray(value) ? value.filter(Boolean).join('；') : value;
}
</script>

<template>
  <div class="preview-block" :class="{ pending: block.status === 'pending' }">
    <template v-if="block.type === 'section'">
      <h4 class="preview-title">{{ block.title }}</h4>
    </template>

    <template v-else-if="block.type === 'teaching_step'">
      <h5 class="preview-title">
        {{ block.title }}
        <span v-if="block.durationMinutes">（{{ block.durationMinutes }}分钟）</span>
      </h5>
    </template>

    <template v-else-if="block.type === 'exercise_group'">
      <h5 class="preview-title">{{ block.title }}</h5>
    </template>

    <template v-else-if="block.type === 'paragraph'">
      <div class="preview-rich-text" v-html="block.content" />
    </template>

    <template v-else-if="block.type === 'list'">
      <ul class="preview-list">
        <li v-for="(item, index) in block.items" :key="`${block.id}-${index}`">
          {{ item }}
        </li>
      </ul>
    </template>

    <template v-else-if="block.type === 'choice_question'">
      <div class="question-preview">
        <div class="preview-rich-text"><strong>选择题：</strong></div>
        <div class="preview-rich-text" v-html="block.prompt" />
        <ul class="preview-list">
          <li v-for="(option, index) in block.options" :key="`${block.id}-${index}`">
            {{ option }}
          </li>
        </ul>
        <div class="muted">答案：{{ renderAnswers(block.answers) || '未填写' }}</div>
        <div class="preview-rich-text" v-html="block.analysis" />
      </div>
    </template>

    <template v-else-if="block.type === 'fill_blank_question'">
      <div class="question-preview">
        <div class="preview-rich-text"><strong>填空题：</strong></div>
        <div class="preview-rich-text" v-html="block.prompt" />
        <div class="muted">答案：{{ renderAnswers(block.answers) || '未填写' }}</div>
        <div class="preview-rich-text" v-html="block.analysis" />
      </div>
    </template>

    <template v-else-if="block.type === 'short_answer_question'">
      <div class="question-preview">
        <div class="preview-rich-text"><strong>简答题：</strong></div>
        <div class="preview-rich-text" v-html="block.prompt" />
        <div class="preview-rich-text"><strong>参考答案：</strong></div>
        <div class="preview-rich-text" v-html="block.referenceAnswer" />
        <div class="preview-rich-text" v-html="block.analysis" />
      </div>
    </template>

    <div
      v-if="block.status === 'pending' && block.suggestion?.kind === 'replace' && block.suggestion.targetBlockId"
      class="muted"
    >
      替换建议，目标 Block：{{ block.suggestion.targetBlockId }}
    </div>

    <div
      v-else-if="block.status === 'pending' && !isContainerBlock(block) && toText(block.type === 'paragraph' ? block.content : '')"
      class="muted"
    >
      AI 待确认
    </div>

    <div v-if="isContainerBlock(block)" class="preview-children">
      <BlockPreview v-for="child in block.children" :key="child.id" :block="child" />
    </div>
  </div>
</template>
