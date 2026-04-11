<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';

import { useFeedbackMutation } from '@/features/settings/composables/useAccount';
import type { FeedbackCreatePayload } from '@/features/settings/types';

import '@/features/feedback/styles/feedback.css';

const route = useRoute();
const feedbackMutation = useFeedbackMutation();

const isOpen = ref(false);
const message = ref('');
const mood = ref<FeedbackCreatePayload['mood']>('happy');
const successMessage = ref('');

const errorMessage = computed(() => {
  if (!feedbackMutation.error.value) {
    return '';
  }
  return '提交反馈失败，请稍后重试。';
});

async function submitFeedback() {
  successMessage.value = '';
  try {
    await feedbackMutation.mutateAsync({
      mood: mood.value,
      message: message.value.trim(),
      page_path: route.fullPath,
    });
    successMessage.value = '反馈已提交，谢谢你的建议。';
    message.value = '';
    mood.value = 'happy';
    window.setTimeout(() => {
      isOpen.value = false;
      successMessage.value = '';
    }, 1600);
  } catch {
    // Inline message handles the error state.
  }
}
</script>

<template>
  <div class="feedback-widget">
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

      <p v-if="successMessage" class="feedback-note success">{{ successMessage }}</p>
      <p v-else-if="errorMessage" class="feedback-note error">{{ errorMessage }}</p>
    </div>
  </div>
</template>
