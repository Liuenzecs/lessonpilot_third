<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useResendVerificationMutation } from '@/features/auth/composables/useAuth';
import { formatAmount, formatBillingDate, formatCountdown } from '@/features/billing/utils';
import {
  useAccount,
  useChangePasswordMutation,
  useCheckoutMutation,
  useCreateInvoiceRequestMutation,
  useDeleteAccountMutation,
  useExportAccountMutation,
  useInvoiceRequests,
  useRenewSubscriptionMutation,
  useStartTrialMutation,
  useSubscription,
  useSubscriptionOrders,
  useUpdateAccountMutation,
} from '@/features/settings/composables/useAccount';
import type { BillingOrderRecord } from '@/features/settings/types';

import '@/features/settings/styles/settings.css';

const router = useRouter();
const authStore = useAuthStore();
const accountQuery = useAccount();
const subscriptionQuery = useSubscription();
const ordersQuery = useSubscriptionOrders();
const invoiceRequestsQuery = useInvoiceRequests();
const updateAccountMutation = useUpdateAccountMutation();
const changePasswordMutation = useChangePasswordMutation();
const exportAccountMutation = useExportAccountMutation();
const deleteAccountMutation = useDeleteAccountMutation();
const resendVerificationMutation = useResendVerificationMutation();
const startTrialMutation = useStartTrialMutation();
const checkoutMutation = useCheckoutMutation();
const renewSubscriptionMutation = useRenewSubscriptionMutation();
const createInvoiceRequestMutation = useCreateInvoiceRequestMutation();

const activeTab = ref<'profile' | 'password' | 'subscription' | 'data'>('subscription');
const profileForm = reactive({ name: '', email: '' });
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});
const billingCycle = ref<'monthly' | 'yearly'>('yearly');
const channel = ref<'wechat' | 'alipay'>('wechat');
const invoiceForm = reactive({
  order_id: '',
  title: '',
  tax_number: '',
  email: '',
  remark: '',
});
const profileMessage = ref('');
const passwordMessage = ref('');
const subscriptionMessage = ref('');
const invoiceMessage = ref('');
const deleteDialogOpen = ref(false);
const deleteConfirmText = ref('');
const deleteError = ref('');

watch(
  () => accountQuery.data.value,
  (account) => {
    if (!account) {
      return;
    }
    profileForm.name = account.name;
    profileForm.email = account.email;
    if (!invoiceForm.email) {
      invoiceForm.email = account.email;
    }
    authStore.setUser(account);
  },
  { immediate: true },
);

watch(
  () => subscriptionQuery.data.value,
  (subscription) => {
    if (!subscription) {
      return;
    }
    billingCycle.value = subscription.billing_cycle ?? 'yearly';
  },
  { immediate: true },
);

watch(
  () => ordersQuery.data.value?.items,
  (items) => {
    const firstPaidOrder = items?.find((item) => item.status === 'paid');
    if (firstPaidOrder && !invoiceForm.order_id) {
      invoiceForm.order_id = firstPaidOrder.id;
    }
  },
  { immediate: true },
);

const account = computed(() => accountQuery.data.value);
const subscription = computed(() => subscriptionQuery.data.value);
const orders = computed(() => ordersQuery.data.value?.items ?? []);
const invoiceRequests = computed(() => invoiceRequestsQuery.data.value?.items ?? []);
const paidOrders = computed(() => orders.value.filter((order) => order.status === 'paid'));
const usagePercent = computed(() => {
  if (!subscription.value?.monthly_task_limit) {
    return 0;
  }
  return Math.min(
    100,
    Math.round((subscription.value.tasks_used_this_month / subscription.value.monthly_task_limit) * 100),
  );
});
const isTrialEligible = computed(
  () => Boolean(subscription.value && subscription.value.status !== 'trialing' && subscription.value.status !== 'active' && !subscription.value.trial_used),
);

async function saveProfile() {
  profileMessage.value = '';
  const payload: { name?: string; email?: string } = {};
  if (profileForm.name.trim() !== account.value?.name) {
    payload.name = profileForm.name.trim();
  }
  if (profileForm.email.trim() !== account.value?.email) {
    payload.email = profileForm.email.trim();
  }
  if (!payload.name && !payload.email) {
    profileMessage.value = '没有需要保存的更改。';
    return;
  }
  const updated = await updateAccountMutation.mutateAsync(payload);
  authStore.setUser(updated);
  profileMessage.value = payload.email ? '个人信息已保存，邮箱已重新进入待验证状态。' : '个人信息已保存。';
}

async function resendVerification() {
  profileMessage.value = '';
  const response = await resendVerificationMutation.mutateAsync();
  profileMessage.value = response.message;
}

async function changePassword() {
  passwordMessage.value = '';
  await changePasswordMutation.mutateAsync(passwordForm);
  passwordMessage.value = '密码已更新。';
  passwordForm.current_password = '';
  passwordForm.new_password = '';
  passwordForm.confirm_password = '';
}

async function startTrial() {
  subscriptionMessage.value = '';
  const response = await startTrialMutation.mutateAsync();
  subscriptionMessage.value = response.message;
}

async function checkoutOrRenew() {
  subscriptionMessage.value = '';
  const payload = {
    plan: 'professional' as const,
    billing_cycle: billingCycle.value,
    channel: channel.value,
  };
  const mutation = subscription.value?.status === 'active' ? renewSubscriptionMutation : checkoutMutation;
  const response = await mutation.mutateAsync(payload);
  if (response.order?.checkout_url && response.order.status === 'pending') {
    window.open(response.order.checkout_url, '_blank', 'noopener,noreferrer');
  }
  subscriptionMessage.value = response.message;
}

async function submitInvoiceRequest() {
  invoiceMessage.value = '';
  await createInvoiceRequestMutation.mutateAsync({
    order_id: invoiceForm.order_id,
    title: invoiceForm.title.trim(),
    tax_number: invoiceForm.tax_number.trim(),
    email: invoiceForm.email.trim(),
    remark: invoiceForm.remark.trim() || null,
  });
  invoiceMessage.value = '发票申请已提交，我们会通过邮件联系你。';
  invoiceForm.title = '';
  invoiceForm.tax_number = '';
  invoiceForm.remark = '';
}

async function exportAccountData() {
  const blob = await exportAccountMutation.mutateAsync();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'lessonpilot-account-export.json';
  anchor.click();
  URL.revokeObjectURL(url);
}

async function confirmDeleteAccount() {
  deleteError.value = '';
  try {
    await deleteAccountMutation.mutateAsync({ confirm_text: deleteConfirmText.value });
    authStore.clearSession();
    await router.push({ name: 'landing' });
  } catch {
    deleteError.value = '删除账户失败，请确认你已经输入 DELETE。';
  }
}

function orderStatusText(order: BillingOrderRecord) {
  if (order.status === 'paid') {
    return '已支付';
  }
  if (order.status === 'expired') {
    return '已过期';
  }
  if (order.status === 'failed') {
    return '支付失败';
  }
  return '待支付';
}
</script>

<template>
  <section class="settings-page">
    <div class="settings-hero">
      <p class="page-eyebrow">账户设置</p>
      <h1 class="page-title">账户设置</h1>
      <p class="subtitle">个人信息、密码安全、真实订阅和数据管理都在这里完成。</p>
    </div>

    <div class="settings-layout">
      <aside class="settings-tabs app-card">
        <button :class="{ active: activeTab === 'profile' }" type="button" @click="activeTab = 'profile'">个人信息</button>
        <button :class="{ active: activeTab === 'password' }" type="button" @click="activeTab = 'password'">密码安全</button>
        <button :class="{ active: activeTab === 'subscription' }" type="button" @click="activeTab = 'subscription'">订阅方案</button>
        <button :class="{ active: activeTab === 'data' }" type="button" @click="activeTab = 'data'">数据管理</button>
      </aside>

      <div class="settings-content">
        <section v-if="activeTab === 'profile'" class="settings-panel app-card">
          <h2>个人信息</h2>
          <label class="field">
            <span>姓名</span>
            <input v-model.trim="profileForm.name" type="text" />
          </label>
          <label class="field">
            <span>邮箱</span>
            <input v-model.trim="profileForm.email" type="email" />
          </label>
          <div class="settings-inline-row">
            <span class="verification-badge" :class="{ verified: account?.email_verified }">
              {{ account?.email_verified ? '已验证' : '未验证' }}
            </span>
            <button
              v-if="account && !account.email_verified"
              class="button ghost"
              type="button"
              :disabled="resendVerificationMutation.isPending.value"
              @click="resendVerification"
            >
              {{ resendVerificationMutation.isPending.value ? '发送中...' : '重新发送验证邮件' }}
            </button>
          </div>
          <button class="button primary" type="button" :disabled="updateAccountMutation.isPending.value" @click="saveProfile">
            {{ updateAccountMutation.isPending.value ? '保存中...' : '保存个人信息' }}
          </button>
          <p v-if="profileMessage" class="feedback success">{{ profileMessage }}</p>
        </section>

        <section v-else-if="activeTab === 'password'" class="settings-panel app-card">
          <h2>密码安全</h2>
          <label class="field">
            <span>当前密码</span>
            <input v-model="passwordForm.current_password" type="password" autocomplete="current-password" />
          </label>
          <label class="field">
            <span>新密码</span>
            <input v-model="passwordForm.new_password" type="password" autocomplete="new-password" />
          </label>
          <label class="field">
            <span>确认新密码</span>
            <input v-model="passwordForm.confirm_password" type="password" autocomplete="new-password" />
          </label>
          <button
            class="button primary"
            type="button"
            :disabled="changePasswordMutation.isPending.value"
            @click="changePassword"
          >
            {{ changePasswordMutation.isPending.value ? '提交中...' : '修改密码' }}
          </button>
          <p v-if="passwordMessage" class="feedback success">{{ passwordMessage }}</p>
        </section>

        <section v-else-if="activeTab === 'subscription'" class="settings-panel app-card">
          <h2>订阅方案</h2>

          <div class="subscription-summary">
            <div>
              <div class="page-eyebrow">当前状态</div>
              <div class="subscription-plan">{{ subscription?.plan_label || '免费版' }}</div>
              <p class="subtitle">
                <template v-if="subscription?.status === 'trialing'">
                  {{ formatCountdown(subscription.trial_ends_at) }}，试用结束前支付不会吞掉试用天数。
                </template>
                <template v-else-if="subscription?.status === 'active'">
                  当前周期到 {{ formatBillingDate(subscription.current_period_end) }}，到期前手动续费即可顺延。
                </template>
                <template v-else-if="subscription?.status === 'expired'">
                  专业版已到期，当前已回到免费版能力。
                </template>
                <template v-else>
                  免费版每月最多新建 5 份教案，超出后需要升级。
                </template>
              </p>
            </div>
            <div class="subscription-pill">{{ subscription?.status || 'free' }}</div>
          </div>

          <div class="subscription-upgrade app-card">
            <h3>专业版计费中心</h3>
            <p>支持 7 天试用、微信/支付宝支付、手动续费和真实订单记录。</p>

            <div class="billing-toggle-row">
              <button :class="{ active: billingCycle === 'monthly' }" type="button" @click="billingCycle = 'monthly'">月付 ¥29</button>
              <button :class="{ active: billingCycle === 'yearly' }" type="button" @click="billingCycle = 'yearly'">年付 ¥228</button>
            </div>

            <div class="billing-toggle-row">
              <button :class="{ active: channel === 'wechat' }" type="button" @click="channel = 'wechat'">微信支付</button>
              <button :class="{ active: channel === 'alipay' }" type="button" @click="channel = 'alipay'">支付宝</button>
            </div>

            <div class="button-row">
              <button
                v-if="isTrialEligible"
                class="button ghost"
                type="button"
                :disabled="startTrialMutation.isPending.value"
                @click="startTrial"
              >
                {{ startTrialMutation.isPending.value ? '试用开启中...' : '开始 7 天试用' }}
              </button>
              <button
                class="button primary"
                type="button"
                :disabled="checkoutMutation.isPending.value || renewSubscriptionMutation.isPending.value"
                @click="checkoutOrRenew"
              >
                {{
                  checkoutMutation.isPending.value || renewSubscriptionMutation.isPending.value
                    ? '处理中...'
                    : subscription?.status === 'active'
                      ? '手动续费'
                      : '立即支付'
                }}
              </button>
            </div>

            <p v-if="subscriptionMessage" class="feedback success">{{ subscriptionMessage }}</p>
          </div>

          <div class="subscription-usage">
            <div class="settings-inline-row">
              <span>
                本月已使用：{{ subscription?.tasks_used_this_month || 0 }}
                <template v-if="subscription?.monthly_task_limit != null">/ {{ subscription?.monthly_task_limit }} 份教案</template>
                <template v-else>· 专业版不限量</template>
              </span>
              <span v-if="subscription?.monthly_task_limit != null">{{ usagePercent }}%</span>
            </div>
            <div v-if="subscription?.monthly_task_limit != null" class="usage-bar">
              <div class="usage-bar-fill" :style="{ width: `${usagePercent}%` }" />
            </div>
          </div>

          <div class="data-card app-card">
            <h3>支付记录</h3>
            <div v-if="ordersQuery.isLoading.value" class="subtitle">正在加载支付记录...</div>
            <div v-else-if="orders.length === 0" class="subtitle">还没有支付记录。</div>
            <div v-else class="billing-records">
              <div v-for="order in orders" :key="order.id" class="billing-record-row">
                <div>
                  <strong>{{ order.billing_cycle === 'monthly' ? '专业版月付' : '专业版年付' }}</strong>
                  <div class="subtitle">{{ order.channel === 'wechat' ? '微信支付' : '支付宝' }} · {{ orderStatusText(order) }}</div>
                </div>
                <div class="billing-record-meta">
                  <strong>{{ formatAmount(order.amount_cents) }}</strong>
                  <div class="subtitle">生效时间：{{ formatBillingDate(order.effective_at) }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="data-card app-card">
            <h3>发票申请</h3>
            <div v-if="paidOrders.length === 0" class="subtitle">完成支付后即可在这里提交发票申请。</div>
            <template v-else>
              <label class="field">
                <span>关联订单</span>
                <select v-model="invoiceForm.order_id">
                  <option v-for="order in paidOrders" :key="order.id" :value="order.id">
                    {{ order.id }} · {{ formatAmount(order.amount_cents) }}
                  </option>
                </select>
              </label>
              <label class="field">
                <span>发票抬头</span>
                <input v-model.trim="invoiceForm.title" type="text" />
              </label>
              <label class="field">
                <span>税号</span>
                <input v-model.trim="invoiceForm.tax_number" type="text" />
              </label>
              <label class="field">
                <span>接收邮箱</span>
                <input v-model.trim="invoiceForm.email" type="email" />
              </label>
              <label class="field">
                <span>备注（可选）</span>
                <textarea v-model.trim="invoiceForm.remark" rows="3" />
              </label>
              <button
                class="button primary"
                type="button"
                :disabled="createInvoiceRequestMutation.isPending.value || !invoiceForm.order_id || !invoiceForm.title || !invoiceForm.tax_number || !invoiceForm.email"
                @click="submitInvoiceRequest"
              >
                {{ createInvoiceRequestMutation.isPending.value ? '提交中...' : '提交发票申请' }}
              </button>
              <p v-if="invoiceMessage" class="feedback success">{{ invoiceMessage }}</p>
            </template>

            <div v-if="invoiceRequests.length" class="invoice-request-list">
              <div v-for="item in invoiceRequests" :key="item.id" class="billing-record-row">
                <div>
                  <strong>{{ item.title }}</strong>
                  <div class="subtitle">{{ item.email }} · {{ item.status === 'submitted' ? '已提交' : item.status }}</div>
                </div>
                <div class="billing-record-meta">
                  <div class="subtitle">订单：{{ item.order_id }}</div>
                  <div class="subtitle">提交于 {{ formatBillingDate(item.created_at) }}</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section v-else class="settings-panel app-card">
          <h2>数据管理</h2>
          <div class="data-card app-card">
            <h3>导出我的数据</h3>
            <p>下载你的账户、任务、文档、历史快照、订阅、订单和发票申请 JSON 备份。</p>
            <button class="button ghost" type="button" :disabled="exportAccountMutation.isPending.value" @click="exportAccountData">
              {{ exportAccountMutation.isPending.value ? '导出中...' : '导出全部数据' }}
            </button>
          </div>

          <div class="data-card danger app-card">
            <h3>删除账户</h3>
            <p>此操作不可恢复，账户、任务、文档、快照、订单和认证数据都会被永久删除。</p>
            <button class="button danger" type="button" @click="deleteDialogOpen = true">删除我的账户</button>
          </div>
        </section>
      </div>
    </div>

    <div v-if="deleteDialogOpen" class="settings-modal-backdrop" @click.self="deleteDialogOpen = false">
      <div class="settings-modal app-card">
        <h2>删除账户</h2>
        <p>请输入 DELETE 以确认永久删除你的账户和全部数据。</p>
        <input v-model.trim="deleteConfirmText" type="text" placeholder="输入 DELETE" />
        <div class="button-row">
          <button class="button ghost" type="button" @click="deleteDialogOpen = false">取消</button>
          <button class="button danger" type="button" :disabled="deleteAccountMutation.isPending.value" @click="confirmDeleteAccount">
            {{ deleteAccountMutation.isPending.value ? '删除中...' : '确认删除' }}
          </button>
        </div>
        <p v-if="deleteError" class="feedback">{{ deleteError }}</p>
      </div>
    </div>
  </section>
</template>
