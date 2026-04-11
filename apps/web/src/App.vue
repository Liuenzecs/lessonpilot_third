<script setup lang="ts">
import { computed } from 'vue';
import { RouterView, useRoute } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import FeedbackWidget from '@/features/feedback/components/FeedbackWidget.vue';

const route = useRoute();
const authStore = useAuthStore();

const showFeedbackWidget = computed(() => authStore.isAuthenticated && route.meta.hideFeedback !== true);
</script>

<template>
  <RouterView />
  <FeedbackWidget v-if="showFeedbackWidget" />
</template>
