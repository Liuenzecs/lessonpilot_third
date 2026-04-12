<script setup lang="ts">
import type { Block } from '@lessonpilot/shared-types';

import { isContainerBlock } from '@lessonpilot/shared-types';
import { computed } from 'vue';

import { getBlockIndent } from '@/shared/utils/content';

defineOptions({
  name: 'BlockPreview',
});

const props = defineProps<{
  block: Block;
}>();

const block = computed(() => props.block);

function toText(value: string): string {
  return value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function renderAnswers(value: string[] | string): string {
  return Array.isArray(value) ? value.filter(Boolean).join('，') : value;
}

function getIndentStyle(block: Block): { marginLeft?: string } {
  if (block.type !== 'paragraph' && block.type !== 'list') {
    return {};
  }

  const indent = getBlockIndent(block);
  return indent > 0 ? { marginLeft: `${indent * 24}px` } : {};
}

function getSuggestionHint(block: Block): string | null {
  if (block.status !== 'pending') {
    return null;
  }

  if (block.suggestion?.kind === 'replace' && block.suggestion.targetBlockId) {
    if (block.suggestion.mode === 'selection') {
      return '替换建议：基于原选中文本生成';
    }
    return '替换建议：将覆盖原有内容';
  }

  return 'AI 待确认';
}
</script>

<template>
  <div class="preview-block" :class="[`type-${block.type}`, { pending: block.status === 'pending' }]">
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
      <div class="preview-rich-text" :style="getIndentStyle(block)" v-html="block.content" />
    </template>

    <template v-else-if="block.type === 'list'">
      <ul class="preview-list" :style="getIndentStyle(block)">
        <li v-for="(item, index) in block.items" :key="`${block.id}-${index}`">
          {{ item }}
        </li>
      </ul>
    </template>

    <template v-else-if="block.type === 'choice_question'">
      <div class="question-preview">
        <div class="preview-question-label">选择题</div>
        <div class="preview-rich-text" v-html="block.prompt" />
        <ul class="preview-list">
          <li v-for="(option, index) in block.options" :key="`${block.id}-${index}`">
            {{ option }}
          </li>
        </ul>
        <div class="muted"><strong>答案：</strong>{{ renderAnswers(block.answers) || '未填写' }}</div>
        <div class="preview-rich-text"><strong>解析：</strong></div>
        <div class="preview-rich-text" v-html="block.analysis" />
      </div>
    </template>

    <template v-else-if="block.type === 'fill_blank_question'">
      <div class="question-preview">
        <div class="preview-question-label">填空题</div>
        <div class="preview-rich-text" v-html="block.prompt" />
        <div class="muted"><strong>答案：</strong>{{ renderAnswers(block.answers) || '未填写' }}</div>
        <div class="preview-rich-text"><strong>解析：</strong></div>
        <div class="preview-rich-text" v-html="block.analysis" />
      </div>
    </template>

    <template v-else-if="block.type === 'short_answer_question'">
      <div class="question-preview">
        <div class="preview-question-label">简答题</div>
        <div class="preview-rich-text" v-html="block.prompt" />
        <div class="preview-rich-text"><strong>参考答案：</strong></div>
        <div class="preview-rich-text" v-html="block.referenceAnswer" />
        <div class="preview-rich-text"><strong>解析：</strong></div>
        <div class="preview-rich-text" v-html="block.analysis" />
      </div>
    </template>

    <div v-if="getSuggestionHint(block)" class="preview-hint">
      {{ getSuggestionHint(block) }}
    </div>

    <div
      v-if="block.suggestion?.mode === 'selection' && block.suggestion.selectionText"
      class="preview-selection-context"
    >
      原选中文本：{{ block.suggestion.selectionText }}
    </div>

    <div v-if="isContainerBlock(block)" class="preview-children">
      <BlockPreview v-for="child in block.children" :key="child.id" :block="child" />
    </div>

    <div
      v-else-if="block.type === 'paragraph' && !toText(block.content)"
      class="preview-hint"
    >
      暂无正文内容
    </div>
  </div>
</template>
