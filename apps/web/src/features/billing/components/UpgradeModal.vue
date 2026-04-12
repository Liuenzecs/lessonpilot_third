<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import { useBillingDialogStore } from '@/app/stores/billing';
import {
  useCheckoutMutation,
  useRenewSubscriptionMutation,
  useStartTrialMutation,
  useSubscription,
} from '@/features/settings/composables/useAccount';
import { formatCountdown } from '@/features/billing/utils';

import '@/features/billing/styles/billing.css';

const billingDialog = useBillingDialogStore();
const subscriptionQuery = useSubscription();
const startTrialMutation = useStartTrialMutation();
const checkoutMutation = useCheckoutMutation();
const renewMutation = useRenewSubscriptionMutation();

const billingCycle = ref<'monthly' | 'yearly'>('yearly');
const channel = ref<'wechat' | 'alipay'>('wechat');
const feedbackMessage = ref('');

watch(
  () => billingDialog.initialCycle,
  (value) => {
    billingCycle.value = value;
  },
  { immediate: true },
);

const subscription = computed(() => subscriptionQuery.data.value);
const isTrialEligible = computed(
  () => subscription.value?.status !== 'trialing' && subscription.value?.status !== 'active' && !subscription.value?.trial_used,
);
const primaryActionLabel = computed(() => {
  if (subscription.value?.status === 'active') {
    return '手动续费';
  }
  if (subscription.value?.status === 'trialing') {
    return '立即支付';
  }
  return '立即支付';
});

async function handleTrial() {
  feedbackMessage.value = '';
  const response = await startTrialMutation.mutateAsync();
  feedbackMessage.value = response.message;
}

async function handleCheckout() {
  feedbackMessage.value = '';
  const payload = {
    plan: 'professional' as const,
    billing_cycle: billingCycle.value,
    channel: channel.value,
  };
  const mutation = subscription.value?.status === 'active' ? renewMutation : checkoutMutation;
  const response = await mutation.mutateAsync(payload);
  if (response.order?.checkout_url && response.order.status === 'pending') {
    window.open(response.order.checkout_url, '_blank', 'noopener,noreferrer');
  }
  feedbackMessage.value = response.message;
}
</script>

<template>
  <div v-if="billingDialog.open" class="billing-modal-backdrop" @click.self="billingDialog.closeDialog()">
    <div class="billing-modal app-card">
      <div class="billing-modal-head">
        <div>
          <h2>{{ billingDialog.title }}</h2>
          <p>{{ billingDialog.description }}</p>
          <p v-if="subscription?.status === 'trialing'" class="billing-status-note">
            当前试用中，{{ formatCountdown(subscription.trial_ends_at) }}。现在支付不会吞掉剩余试用天数。
          </p>
          <p v-else-if="subscription?.status === 'active'" class="billing-status-note">
            当前专业版有效期至 {{ subscription.current_period_end ? new Date(subscription.current_period_end).toLocaleString() : '未设置' }}。
          </p>
        </div>
        <button class="button ghost" type="button" @click="billingDialog.closeDialog()">关闭</button>
      </div>

      <div class="billing-choice-row">
        <button class="billing-choice-card" :class="{ active: billingCycle === 'monthly' }" type="button" @click="billingCycle = 'monthly'">
          <strong>月付 ¥29</strong>
          <small>适合先按月体验</small>
        </button>
        <button class="billing-choice-card" :class="{ active: billingCycle === 'yearly' }" type="button" @click="billingCycle = 'yearly'">
          <strong>年付 ¥228</strong>
          <small>折合 ¥19/月，更适合长期使用</small>
        </button>
      </div>

      <div class="billing-choice-row">
        <button class="billing-choice-card" :class="{ active: channel === 'wechat' }" type="button" @click="channel = 'wechat'">
          <strong>微信支付</strong>
          <small>适合移动端完成付款</small>
        </button>
        <button class="billing-choice-card" :class="{ active: channel === 'alipay' }" type="button" @click="channel = 'alipay'">
          <strong>支付宝</strong>
          <small>适合网页端快速付款</small>
        </button>
      </div>

      <ul class="billing-entitlements">
        <li>不限量新建教案与复制为新教案</li>
        <li>局部 AI 重写、AI 补充内容、章节重新生成</li>
        <li>Word + PDF 导出、版本历史、完整专业备课链路</li>
        <li>不自动续费，到期前手动续费即可顺延</li>
      </ul>

      <p v-if="feedbackMessage" class="feedback success">{{ feedbackMessage }}</p>

      <div class="billing-modal-foot">
        <button
          v-if="isTrialEligible"
          class="button ghost"
          type="button"
          :disabled="startTrialMutation.isPending.value"
          @click="handleTrial"
        >
          {{ startTrialMutation.isPending.value ? '试用开启中...' : '开始 7 天试用' }}
        </button>
        <button
          class="button primary"
          type="button"
          :disabled="checkoutMutation.isPending.value || renewMutation.isPending.value"
          @click="handleCheckout"
        >
          {{ checkoutMutation.isPending.value || renewMutation.isPending.value ? '处理中...' : primaryActionLabel }}
        </button>
      </div>
    </div>
  </div>
</template>
