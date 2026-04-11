<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { useResendVerificationMutation } from '@/features/auth/composables/useAuth';
import {
  useAccount,
  useChangePasswordMutation,
  useDeleteAccountMutation,
  useExportAccountMutation,
  useSubscription,
  useUpdateAccountMutation,
} from '@/features/settings/composables/useAccount';

import '@/features/settings/styles/settings.css';

const router = useRouter();
const authStore = useAuthStore();
const accountQuery = useAccount();
const subscriptionQuery = useSubscription();
const updateAccountMutation = useUpdateAccountMutation();
const changePasswordMutation = useChangePasswordMutation();
const exportAccountMutation = useExportAccountMutation();
const deleteAccountMutation = useDeleteAccountMutation();
const resendVerificationMutation = useResendVerificationMutation();

const activeTab = ref<'profile' | 'password' | 'subscription' | 'data'>('profile');
const profileForm = reactive({ name: '', email: '' });
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});
const profileMessage = ref('');
const passwordMessage = ref('');
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
    authStore.setUser(account);
  },
  { immediate: true },
);

const account = computed(() => accountQuery.data.value);
const subscription = computed(() => subscriptionQuery.data.value);
const usagePercent = computed(() => {
  if (!subscription.value?.monthly_task_limit) {
    return 0;
  }
  return Math.min(
    100,
    Math.round((subscription.value.tasks_used_this_month / subscription.value.monthly_task_limit) * 100),
  );
});

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
</script>

<template>
  <section class="settings-page">
    <div class="settings-hero">
      <p class="page-eyebrow">账户设置</p>
      <h1 class="page-title">账户设置</h1>
      <p class="subtitle">个人信息、密码安全、订阅展示和数据管理都在这里完成。</p>
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
              {{ account?.email_verified ? '已验证 ✓' : '未验证' }}
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
              <div class="page-eyebrow">当前方案</div>
              <div class="subscription-plan">{{ subscription?.plan_label || '免费版' }}</div>
            </div>
            <div class="subscription-pill">展示层，不触发真实扣费</div>
          </div>

          <div class="subscription-upgrade app-card">
            <h3>升级到专业版</h3>
            <p>¥29/月，解锁无限生成、局部 AI 重写、PDF 导出和完整历史版本。</p>
            <button class="button primary" type="button">立即升级</button>
          </div>

          <div class="subscription-usage">
            <div class="settings-inline-row">
              <span>本月已使用：{{ subscription?.tasks_used_this_month || 0 }} / {{ subscription?.monthly_task_limit || 5 }} 份教案</span>
              <span>{{ usagePercent }}%</span>
            </div>
            <div class="usage-bar">
              <div class="usage-bar-fill" :style="{ width: `${usagePercent}%` }" />
            </div>
          </div>
        </section>

        <section v-else class="settings-panel app-card">
          <h2>数据管理</h2>
          <div class="data-card app-card">
            <h3>导出我的数据</h3>
            <p>下载你所有任务、文档、历史版本和反馈记录的 JSON 备份。</p>
            <button class="button ghost" type="button" :disabled="exportAccountMutation.isPending.value" @click="exportAccountData">
              {{ exportAccountMutation.isPending.value ? '导出中...' : '导出全部数据' }}
            </button>
          </div>

          <div class="data-card danger app-card">
            <h3>删除账户</h3>
            <p>此操作不可恢复，所有数据将被永久删除。</p>
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
