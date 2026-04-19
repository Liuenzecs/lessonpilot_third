<script setup lang="ts">
/**
 * 可折叠的 Section 面板。
 * 折叠时只显示标题和 status 徽标；
 * 展开时渲染对应 section 类型的编辑器。
 */
import type {
  AssessmentItem,
  CitationReference,
  KeyPoints,
  SectionInfo,
  TeachingObjective,
  TeachingProcessStep,
} from '@lessonpilot/shared-types';
import { computed } from 'vue';

import CitationTooltip from './CitationTooltip.vue';
import KeyPointsEditor from './SectionEditors/KeyPointsEditor.vue';
import GenericListEditor from './SectionEditors/GenericListEditor.vue';
import ObjectivesEditor from './SectionEditors/ObjectivesEditor.vue';
import RichTextEditor from './SectionEditors/RichTextEditor.vue';
import TeachingProcessEditor from './SectionEditors/TeachingProcessEditor.vue';
import AssessmentEditor from './SectionEditors/AssessmentEditor.vue';
import SectionAiActions from './SectionAiActions.vue';
import { stripCitations } from '../utils/citation';

const props = defineProps<{
  section: SectionInfo;
  docType: string;
  sectionData: unknown;
  sectionReferences: CitationReference[];
  collapsed: boolean;
  streamingText: string;
  isRewriting: boolean;
}>();

const emit = defineEmits<{
  'toggle-collapse': [];
  'update-section': [value: unknown];
  confirm: [];
  'ai-action': [payload: { action: 'rewrite' | 'expand' | 'simplify'; instruction: string }];
}>();

const statusLabel = computed(() =>
  props.section.status === 'pending' ? '待确认' : '已确认',
);

const statusClass = computed(() =>
  props.section.status === 'pending' ? 'status-pending' : 'status-confirmed',
);
</script>

<template>
  <div class="section-panel" :class="{ collapsed, rewriting: isRewriting }">
    <div class="section-header" @click="emit('toggle-collapse')">
      <button type="button" class="collapse-toggle" :title="collapsed ? '展开' : '折叠'">
        <span class="collapse-icon">{{ collapsed ? '▸' : '▾' }}</span>
      </button>
      <h3 class="section-title">{{ section.title }}</h3>
      <span class="status-badge" :class="statusClass">{{ statusLabel }}</span>
      <div class="section-actions" @click.stop>
        <button
          v-if="section.status === 'pending'"
          type="button"
          class="confirm-btn"
          @click="emit('confirm')"
        >
          确认
        </button>
        <SectionAiActions
          :disabled="isRewriting"
          @action="emit('ai-action', $event)"
        />
      </div>
    </div>

    <div v-if="!collapsed" class="section-body">
      <div v-if="sectionReferences.length" class="section-references">
        <span class="section-references-label">参考资料</span>
        <CitationTooltip
          v-for="reference in sectionReferences"
          :key="reference.chunk_id"
          :source="reference.source"
          :title="reference.title"
          :chapter="reference.chapter"
          :snippet="reference.content_snippet"
        />
      </div>

      <!-- 流式输出显示区 -->
      <div v-if="streamingText" class="streaming-content">
        <span class="streaming-text">{{ stripCitations(streamingText) }}</span>
        <span class="streaming-cursor" />
      </div>

      <!-- 教案编辑器 -->
      <template v-if="docType === 'lesson_plan'">
        <!-- 教学目标 -->
        <ObjectivesEditor
          v-if="section.name === 'objectives'"
          :model-value="(sectionData as TeachingObjective[])"
          @update:model-value="emit('update-section', $event)"
        />
        <!-- 教学重难点 -->
        <KeyPointsEditor
          v-else-if="section.name === 'key_points'"
          :model-value="(sectionData as KeyPoints)"
          @update:model-value="emit('update-section', $event)"
        />
        <!-- 教学准备 -->
        <GenericListEditor
          v-else-if="section.name === 'preparation'"
          :model-value="(sectionData as string[])"
          placeholder="请输入教学准备内容"
          @update:model-value="emit('update-section', $event)"
        />
        <!-- 教学过程 -->
        <TeachingProcessEditor
          v-else-if="section.name === 'teaching_process'"
          :model-value="(sectionData as TeachingProcessStep[])"
          @update:model-value="emit('update-section', $event)"
        />
        <!-- 板书设计 / 教学反思 -->
        <RichTextEditor
          v-else
          :model-value="(sectionData as string)"
          :placeholder="section.title"
          @update:model-value="emit('update-section', $event)"
        />
      </template>

      <!-- 学案编辑器 -->
      <template v-if="docType === 'study_guide'">
        <!-- 学习目标 / 重点难点 / 知识链接 -->
        <GenericListEditor
          v-if="['learning_objectives', 'key_difficulties', 'prior_knowledge'].includes(section.name)"
          :model-value="(sectionData as string[])"
          :placeholder="section.title"
          @update:model-value="emit('update-section', $event)"
        />
        <AssessmentEditor
          v-else-if="['self_study', 'collaboration', 'presentation', 'assessment', 'extension'].includes(section.name)"
          :model-value="(sectionData as AssessmentItem[])"
          @update:model-value="emit('update-section', $event)"
        />
        <!-- 自主反思 -->
        <RichTextEditor
          v-else
          :model-value="(sectionData as string)"
          :placeholder="section.title"
          @update:model-value="emit('update-section', $event)"
        />
      </template>
    </div>
  </div>
</template>
