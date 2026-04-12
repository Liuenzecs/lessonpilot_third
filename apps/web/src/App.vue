<script setup lang="ts">
import { computed, watch } from 'vue';
import { RouterView, useRoute, useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useBillingDialogStore } from '@/app/stores/billing';
import UpgradeModal from '@/features/billing/components/UpgradeModal.vue';
import FeedbackWidget from '@/features/feedback/components/FeedbackWidget.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const billingDialog = useBillingDialogStore();

const showFeedbackWidget = computed(() => authStore.isAuthenticated && route.meta.hideFeedback !== true);

watch(
  () => [authStore.isAuthenticated, route.query.upgrade, route.query.cycle] as const,
  ([isAuthenticated, upgrade, cycle]) => {
    if (!isAuthenticated || upgrade !== '1') {
      return;
    }

    billingDialog.openDialog({
      reason: 'upgrade',
      title: '继续升级到专业版',
      description: '完成试用或支付后，就能继续使用专业版能力。',
      initialCycle: cycle === 'monthly' ? 'monthly' : 'yearly',
    });

    const nextQuery = { ...route.query };
    delete nextQuery.upgrade;
    delete nextQuery.cycle;
    void router.replace({ query: nextQuery });
  },
  { immediate: true },
);
</script>

<template>
  <RouterView />
  <FeedbackWidget v-if="showFeedbackWidget" />
  <UpgradeModal v-if="authStore.isAuthenticated" />
</template>
