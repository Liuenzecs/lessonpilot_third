<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';

import { useFeedbackMutation } from '@/features/settings/composables/useAccount';
import type { FeedbackCreatePayload } from '@/features/settings/types';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';

import '@/features/feedback/styles/feedback.css';

const route = useRoute();
const feedbackMutation = useFeedbackMutation();
const toast = useToast();

const rootRef = ref<HTMLElement | null>(null);
const isOpen = ref(false);
const message = ref('');
const mood = ref<FeedbackCreatePayload['mood']>('happy');
const errorMessage = computed(() => feedbackMutation.error.value);

function resetComposer() {
  message.value = '';
  mood.value = 'happy';
}

function closePanel() {
  isOpen.value = false;
}

function handleOutsideClick(event: MouseEvent) {
  if (!rootRef.value?.contains(event.target as Node)) {
    closePanel();
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    closePanel();
  }
}

async function submitFeedback() {
  try {
    await feedbackMutation.mutateAsync({
      mood: mood.value,
      message: message.value.trim(),
      page_path: route.fullPath,
    });
    toast.success('反馈已提交', '谢谢你的建议，我们会继续打磨体验。');
    resetComposer();
    closePanel();
  } catch (error) {
    toast.error('提交反馈失败', getErrorDescription(error, '请稍后重试。'));
  }
}

watch(
  () => route.fullPath,
  () => {
    closePanel();
  },
);

onMounted(() => {
  document.addEventListener('click', handleOutsideClick);
  window.addEventListener('keydown', handleKeydown);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick);
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
  <div ref="rootRef" class="feedback-widget">
    <button class="feedback-trigger" type="button" @click="isOpen = !isOpen">💬</button>

    <div v-if="isOpen" class="feedback-panel app-card">
      <div class="feedback-panel-title">反馈与建议</div>
      <textarea
        v-model.trim="message"
        class="feedback-textarea"
        placeholder="说说你的想法..."
      />

      <div class="feedback-mood-row">
        <button
          class="feedback-mood-button"
          :class="{ active: mood === 'happy' }"
          type="button"
          @click="mood = 'happy'"
        >
          😊
        </button>
        <button
          class="feedback-mood-button"
          :class="{ active: mood === 'neutral' }"
          type="button"
          @click="mood = 'neutral'"
        >
          😐
        </button>
        <button
          class="feedback-mood-button"
          :class="{ active: mood === 'sad' }"
          type="button"
          @click="mood = 'sad'"
        >
          😞
        </button>
      </div>

      <button
        class="button primary feedback-submit"
        type="button"
        :disabled="feedbackMutation.isPending.value || !message.trim()"
        @click="submitFeedback"
      >
        {{ feedbackMutation.isPending.value ? '提交中...' : '提交反馈' }}
      </button>

      <p v-if="errorMessage" class="feedback-note error">提交反馈失败，请稍后重试。</p>
    </div>
  </div>
</template>
