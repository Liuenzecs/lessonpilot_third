<script setup lang="ts">
import type { TeachingPackageRecord } from '@/features/editor/types';

defineProps<{
  visible: boolean;
  loading: boolean;
  packageResult: TeachingPackageRecord | null;
}>();

defineEmits<{
  generate: [];
}>();
</script>

<template>
  <section v-if="visible" class="teaching-package-panel">
    <div class="teaching-package-head">
      <div>
        <p class="page-eyebrow">上课包</p>
        <h3>从教案继续整理课堂材料</h3>
      </div>
      <button class="button secondary" type="button" :disabled="loading" @click="$emit('generate')">
        {{ loading ? '正在整理...' : '生成上课包' }}
      </button>
    </div>

    <div v-if="packageResult" class="teaching-package-grid">
      <article>
        <h4>学案草稿</h4>
        <p>{{ packageResult.content.study_guide.learning_objectives.length }} 条学习目标，默认待确认。</p>
      </article>
      <article>
        <h4>PPT 大纲</h4>
        <p>{{ packageResult.content.ppt_outline.length }} 页课件文案，可复制到课件工具。</p>
      </article>
      <article>
        <h4>课堂口播稿</h4>
        <p>{{ packageResult.content.talk_script.questions.length }} 个课堂问题，含导入语和小结语。</p>
      </article>
    </div>

    <p v-else class="teaching-package-note">
      教学目标、重难点和教学过程确认后，可以继续生成学案、PPT 大纲和课堂口播稿。
    </p>
  </section>
</template>
