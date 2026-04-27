<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

import { useCreateTaskMutation, usePersonalAssetRecommendations } from '@/features/task/composables/useTasks';
import type { LessonCategory, LessonType, Scene } from '@lessonpilot/shared-types';
import type { TemplateRecord } from '@/features/task/types';
import { ApiError } from '@/shared/api/client';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';
import {
  GRADE_OPTIONS,
  LESSON_CATEGORY_OPTIONS,
  LESSON_TYPE_OPTIONS,
  SCENE_OPTIONS,
  SUBJECT_OPTIONS,
} from '@/shared/constants/options';
import { request } from '@/shared/api/client';

import '@/features/task/styles/workspace.css';

const router = useRouter();
const createTaskMutation = useCreateTaskMutation();
const toast = useToast();

const submitError = ref('');
const form = reactive({
  subject: '',
  grade: '',
  topic: '',
  class_hour: 1,
  lesson_category: 'new' as LessonCategory,
  lesson_type: 'lesson_plan' as LessonType,
  scene: 'public_school' as Scene,
  requirements: '',
  template_id: null as string | null,
});

const templates = ref<TemplateRecord[]>([]);
const templatesLoading = ref(false);
const usePersonalAssets = ref(false);
const selectedPersonalAssetIds = ref<string[]>([]);
const assetRecommendationsQuery = usePersonalAssetRecommendations(() => ({
  subject: form.subject,
  grade: form.grade,
  topic: form.topic,
  keywords: form.requirements,
}));

async function fetchTemplates() {
  if (!form.subject) {
    templates.value = [];
    return;
  }
  templatesLoading.value = true;
  try {
    const templateType = form.lesson_type === 'study_guide' ? 'study_guide' : 'lesson_plan';
    templates.value = await request<TemplateRecord[]>(
      `/api/v1/templates/?subject=${encodeURIComponent(form.subject)}&template_type=${templateType}`,
    );
  } catch {
    templates.value = [];
  } finally {
    templatesLoading.value = false;
  }
}

watch(() => form.subject, () => {
  form.template_id = null;
  void fetchTemplates();
});

watch(() => form.lesson_type, () => {
  form.template_id = null;
  void fetchTemplates();
});

const canSubmit = computed(() => Boolean(form.subject) && Boolean(form.grade) && form.topic.trim().length > 0);

async function submit() {
  submitError.value = '';

  try {
    const task = await createTaskMutation.mutateAsync({
      ...form,
      requirements: form.requirements.trim() || null,
    });
    toast.info('已进入编辑器，正在整理初稿…', '内容会逐节写入编辑器。');
    await router.push({
      name: 'editor',
      params: { taskId: task.id },
      query: usePersonalAssets.value
        ? {
            usePersonalAssets: '1',
            personalAssetIds: selectedPersonalAssetIds.value.join(','),
          }
        : undefined,
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      submitError.value = '登录状态已失效，请重新登录后再试。';
      toast.error('登录状态已失效', '请重新登录后再创建教案。');
      return;
    }

    submitError.value = '创建备课任务失败，请稍后重试。';
    toast.error('创建备课任务失败', getErrorDescription(error, '请稍后重试。'));
  }
}

function togglePersonalAsset(assetId: string) {
  if (selectedPersonalAssetIds.value.includes(assetId)) {
    selectedPersonalAssetIds.value = selectedPersonalAssetIds.value.filter((id) => id !== assetId);
    return;
  }
  selectedPersonalAssetIds.value = [...selectedPersonalAssetIds.value, assetId];
}
</script>

<template>
  <div class="page-shell create-page">
    <div class="create-frame app-card">
      <div class="create-head">
        <div class="create-head-actions">
          <button class="button ghost" type="button" @click="router.push({ name: 'tasks' })">
            ← 返回备课台
          </button>
          <button class="button secondary" type="button" @click="router.push({ name: 'task-import' })">
            导入旧教案
          </button>
        </div>
        <div class="create-head-copy">
          <p class="page-eyebrow">创建备课</p>
          <h1 class="page-title">开始一份新备课</h1>
          <p class="subtitle">先确定学科、年级和课题，系统会按 section 逐节整理初稿并实时写入编辑器。</p>
        </div>
      </div>

      <form class="create-body" @submit.prevent="submit">
        <!-- 基本信息行 -->
        <div class="create-row">
          <div class="create-field">
            <label class="create-label">学科</label>
            <div class="create-choice-grid compact">
              <button
                v-for="subject in SUBJECT_OPTIONS"
                :key="subject"
                type="button"
                class="wizard-choice-card"
                :class="{ active: form.subject === subject }"
                @click="form.subject = subject"
              >
                {{ subject }}
              </button>
            </div>
          </div>

          <div class="create-field">
            <label class="create-label">年级</label>
            <div class="create-choice-grid compact">
              <button
                v-for="grade in GRADE_OPTIONS"
                :key="grade"
                type="button"
                class="wizard-choice-card"
                :class="{ active: form.grade === grade }"
                @click="form.grade = grade"
              >
                {{ grade }}
              </button>
            </div>
          </div>
        </div>

        <!-- 课题 + 课时 -->
        <div class="create-row">
          <div class="create-field grow">
            <label class="create-label">课题主题 <span class="required">*</span></label>
            <input
              v-model.trim="form.topic"
              class="create-input"
              type="text"
              placeholder="例如：《春》—— 朱自清"
            />
          </div>

          <div class="create-field shrink">
            <label class="create-label">课时</label>
            <input
              v-model.number="form.class_hour"
              class="create-input"
              type="number"
              min="1"
              max="10"
            />
          </div>
        </div>

        <!-- 课型 -->
        <div class="create-field">
          <label class="create-label">课型</label>
          <div class="create-choice-grid inline">
            <button
              v-for="opt in LESSON_CATEGORY_OPTIONS"
              :key="opt.value"
              type="button"
              class="wizard-choice-card"
              :class="{ active: form.lesson_category === opt.value }"
              @click="form.lesson_category = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- 文档类型 -->
        <div class="create-field">
          <label class="create-label">文档类型</label>
          <div class="create-toggle-group">
            <button
              v-for="opt in LESSON_TYPE_OPTIONS"
              :key="opt.value"
              type="button"
              class="create-toggle-btn"
              :class="{ active: form.lesson_type === opt.value }"
              @click="form.lesson_type = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- 使用场景 -->
        <div class="create-field">
          <label class="create-label">使用场景</label>
          <div class="create-choice-grid inline">
            <button
              v-for="opt in SCENE_OPTIONS"
              :key="opt.value"
              type="button"
              class="wizard-choice-card"
              :class="{ active: form.scene === opt.value }"
              @click="form.scene = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- 模板选择 -->
        <div v-if="templates.length > 0" class="create-field">
          <label class="create-label">选择模板（可选）</label>
          <p v-if="templatesLoading" class="create-helper">正在匹配可用模板…</p>
          <p v-else class="create-helper">不选择也可以，系统会根据学科与文档类型自动匹配。</p>
          <div class="template-choice-grid">
            <button
              type="button"
              class="template-card"
              :class="{ active: form.template_id === null }"
              @click="form.template_id = null"
            >
              <span class="template-card-name">系统推荐</span>
              <span class="template-card-desc">根据当前场景匹配更合适的模板</span>
            </button>
            <button
              v-for="tpl in templates"
              :key="tpl.id"
              type="button"
              class="template-card"
              :class="{ active: form.template_id === tpl.id }"
              @click="form.template_id = tpl.id"
            >
              <span class="template-card-name">{{ tpl.name }}</span>
              <span class="template-card-desc">{{ tpl.description }}</span>
            </button>
          </div>
        </div>

        <div class="create-field personal-assets-field">
          <label class="create-label">个人资料库（可选）</label>
          <label class="create-checkbox-line">
            <input v-model="usePersonalAssets" type="checkbox" />
            <span>整理初稿时参考我的资料库</span>
          </label>
          <p class="create-helper">系统会按课题推荐当前账号的旧教案、讲义或 PPT 大纲。</p>
          <div v-if="usePersonalAssets" class="template-choice-grid">
            <button
              v-for="asset in assetRecommendationsQuery.data.value ?? []"
              :key="asset.asset_id"
              type="button"
              class="template-card"
              :class="{ active: selectedPersonalAssetIds.includes(asset.asset_id) }"
              @click="togglePersonalAsset(asset.asset_id)"
            >
              <span class="template-card-name">{{ asset.title }}</span>
              <span class="template-card-desc">{{ asset.section_title }} · {{ asset.file_type }}</span>
            </button>
          </div>
          <p v-if="usePersonalAssets && !(assetRecommendationsQuery.data.value ?? []).length" class="create-helper">
            当前课题暂未匹配到个人资料；仍可开启，生成时会自动提示未命中。
          </p>
        </div>

        <!-- 补充说明 -->
        <div class="create-field">
          <label class="create-label">补充说明（可选）</label>
          <textarea
            v-model.trim="form.requirements"
            class="create-textarea"
            rows="3"
            placeholder="例如：重点讲解配方法，练习部分增加一题分层题。"
          />
        </div>

        <p v-if="submitError" class="feedback">{{ submitError }}</p>

        <!-- 提交 -->
        <div class="create-foot">
          <button
            class="button primary"
            type="submit"
            :disabled="!canSubmit || createTaskMutation.isPending.value"
          >
            {{ createTaskMutation.isPending.value ? '正在创建...' : '开始备课' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
