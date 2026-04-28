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
  useStyleProfile,
  useUpdateAccountMutation,
  useUpdateStyleProfileMutation,
} from '@/features/settings/composables/useAccount';
import { getAppErrorState, getErrorDescription } from '@/shared/api/errors';
import StatePanel from '@/shared/components/StatePanel.vue';
import { useToast } from '@/shared/composables/useToast';

import '@/features/settings/styles/settings.css';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();
const accountQuery = useAccount();
const updateAccountMutation = useUpdateAccountMutation();
const changePasswordMutation = useChangePasswordMutation();
const exportAccountMutation = useExportAccountMutation();
const deleteAccountMutation = useDeleteAccountMutation();
const styleProfileQuery = useStyleProfile();
const updateStyleProfileMutation = useUpdateStyleProfileMutation();
const resendVerificationMutation = useResendVerificationMutation();

const activeTab = ref<'profile' | 'style' | 'password' | 'data'>('profile');
const profileForm = reactive({ name: '', email: '' });
const styleForm = reactive({
  enabled: true,
  objective_style: '',
  process_style: '',
  school_wording: '',
  activity_preferences: '',
  avoid_phrases: '',
});
const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});
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

watch(
  () => styleProfileQuery.data.value,
  (profile) => {
    if (!profile) {
      return;
    }
    styleForm.enabled = profile.enabled;
    styleForm.objective_style = profile.objective_style;
    styleForm.process_style = profile.process_style;
    styleForm.school_wording = profile.school_wording;
    styleForm.activity_preferences = profile.activity_preferences;
    styleForm.avoid_phrases = profile.avoid_phrases;
  },
  { immediate: true },
);

const account = computed(() => accountQuery.data.value);
const settingsErrorState = computed(() => {
  if (account.value) {
    return null;
  }

  const error = accountQuery.error.value;
  if (!error) {
    return null;
  }

  return getAppErrorState(error, {
    defaultTitle: '账户设置暂时打不开',
    defaultDescription: '你可以重试，或者先去帮助中心看看。',
  });
});
const showProfileSkeleton = computed(() => activeTab.value === 'profile' && accountQuery.isLoading.value && !account.value);
const showStyleSkeleton = computed(() => activeTab.value === 'style' && styleProfileQuery.isLoading.value);
const showPasswordSkeleton = computed(() => activeTab.value === 'password' && accountQuery.isLoading.value && !account.value);
const showDataSkeleton = computed(() => activeTab.value === 'data' && accountQuery.isLoading.value && !account.value);

async function saveProfile() {
  const payload: { name?: string; email?: string } = {};
  if (profileForm.name.trim() !== account.value?.name) {
    payload.name = profileForm.name.trim();
  }
  if (profileForm.email.trim() !== account.value?.email) {
    payload.email = profileForm.email.trim();
  }
  if (!payload.name && !payload.email) {
    toast.info('没有需要保存的更改');
    return;
  }

  try {
    const updated = await updateAccountMutation.mutateAsync(payload);
    authStore.setUser(updated);
    toast.success(
      '个人信息已保存',
      payload.email ? '邮箱已重新进入待验证状态，请留意新的验证邮件。' : '新的资料已经同步到当前账户。',
    );
  } catch (error) {
    toast.error('保存个人信息失败', getErrorDescription(error, '请稍后重试。'));
  }
}

async function saveStyleProfile() {
  try {
    await updateStyleProfileMutation.mutateAsync({ ...styleForm });
    toast.success('风格记忆已保存', styleForm.enabled ? '后续生成会参考这些表达偏好。' : '已关闭个人风格注入。');
  } catch (error) {
    toast.error('保存风格记忆失败', getErrorDescription(error, '请稍后重试。'));
  }
}

async function resendVerification() {
  try {
    const response = await resendVerificationMutation.mutateAsync();
    toast.success('验证邮件已发送', response.message);
  } catch (error) {
    toast.error('发送验证邮件失败', getErrorDescription(error, '请稍后重试。'));
  }
}

async function changePassword() {
  try {
    await changePasswordMutation.mutateAsync(passwordForm);
    toast.success('密码已更新');
    passwordForm.current_password = '';
    passwordForm.new_password = '';
    passwordForm.confirm_password = '';
  } catch (error) {
    toast.error('修改密码失败', getErrorDescription(error, '请检查当前密码和新密码后重试。'));
  }
}

async function exportAccountData() {
  try {
    const blob = await exportAccountMutation.mutateAsync();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'lessonpilot-account-export.json';
    anchor.click();
    URL.revokeObjectURL(url);
    toast.success('数据导出已开始');
  } catch (error) {
    toast.error('导出数据失败', getErrorDescription(error, '请稍后重试。'));
  }
}

async function confirmDeleteAccount() {
  deleteError.value = '';

  try {
    await deleteAccountMutation.mutateAsync({ confirm_text: deleteConfirmText.value });
    authStore.clearSession();
    toast.success('账户已删除');
    await router.push({ name: 'landing' });
  } catch {
    deleteError.value = '删除账户失败，请确认你已经输入 DELETE。';
    toast.error('删除账户失败', '请确认你已经输入 DELETE。');
  }
}
</script>

<template>
  <section class="settings-page">
    <div class="settings-hero">
      <p class="page-eyebrow">账户设置</p>
      <h1 class="page-title">账户设置</h1>
      <p class="subtitle">个人信息、密码安全和数据管理都在这里完成。</p>
    </div>

    <div class="settings-layout">
      <aside class="settings-tabs app-card">
        <button :class="{ active: activeTab === 'profile' }" type="button" @click="activeTab = 'profile'">个人信息</button>
        <button :class="{ active: activeTab === 'style' }" type="button" @click="activeTab = 'style'">风格记忆</button>
        <button :class="{ active: activeTab === 'password' }" type="button" @click="activeTab = 'password'">密码安全</button>
        <button :class="{ active: activeTab === 'data' }" type="button" @click="activeTab = 'data'">数据管理</button>
      </aside>

      <div class="settings-content">
        <StatePanel
          v-if="settingsErrorState"
          icon="⚙"
          eyebrow="账户设置"
          :title="settingsErrorState.title"
          :description="settingsErrorState.description"
          tone="error"
        >
          <template #actions>
            <button class="button primary" type="button" @click="accountQuery.refetch()">重试</button>
            <button class="button ghost" type="button" @click="router.push({ name: 'help' })">去帮助中心</button>
          </template>
        </StatePanel>

        <section v-else-if="showProfileSkeleton || showStyleSkeleton || showPasswordSkeleton || showDataSkeleton" class="settings-panel app-card settings-skeleton-panel">
          <div class="settings-skeleton-line short" />
          <div class="settings-skeleton-line" />
          <div class="settings-skeleton-card" />
          <div class="settings-skeleton-card" />
        </section>

        <section v-else-if="activeTab === 'profile'" class="settings-panel app-card">
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
        </section>

        <section v-else-if="activeTab === 'style'" class="settings-panel app-card">
          <div class="settings-panel-heading">
            <div>
              <h2>风格记忆</h2>
              <p>保存你常用的目标写法、过程风格和学校措辞。它只影响生成参考，不会替你自动确认内容。</p>
            </div>
            <label class="settings-switch">
              <input v-model="styleForm.enabled" type="checkbox" />
              <span>{{ styleForm.enabled ? '已启用' : '已关闭' }}</span>
            </label>
          </div>

          <label class="field">
            <span>教学目标写法</span>
            <textarea
              v-model.trim="styleForm.objective_style"
              rows="3"
              placeholder="例如：目标要以“通过……，学生能够……”开头，强调可观察、可评价。"
            />
          </label>

          <label class="field">
            <span>教学过程风格</span>
            <textarea
              v-model.trim="styleForm.process_style"
              rows="3"
              placeholder="例如：每个环节写清教师追问、学生批注和小组交流，设计意图要贴近课堂真实操作。"
            />
          </label>

          <label class="field">
            <span>学校提交措辞</span>
            <textarea
              v-model.trim="styleForm.school_wording"
              rows="3"
              placeholder="例如：使用“学习任务群”“核心素养”“朗读品味”等学校常用表达。"
            />
          </label>

          <label class="field">
            <span>常用课堂活动</span>
            <textarea
              v-model.trim="styleForm.activity_preferences"
              rows="3"
              placeholder="例如：情境导入、圈点批注、同桌互说、板书归纳、当堂检测。"
            />
          </label>

          <label class="field">
            <span>尽量避免的套话</span>
            <textarea
              v-model.trim="styleForm.avoid_phrases"
              rows="3"
              placeholder="例如：避免“提高学生综合素质”“培养学习兴趣”等空泛表述。"
            />
          </label>

          <button
            class="button primary"
            type="button"
            :disabled="updateStyleProfileMutation.isPending.value"
            @click="saveStyleProfile"
          >
            {{ updateStyleProfileMutation.isPending.value ? '保存中...' : '保存风格记忆' }}
          </button>
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
        </section>

        <section v-else class="settings-panel app-card">
          <h2>数据管理</h2>
          <div class="data-card app-card">
            <h3>导出我的数据</h3>
            <p>下载你的账户、任务和文档 JSON 备份。</p>
            <button class="button ghost" type="button" :disabled="exportAccountMutation.isPending.value" @click="exportAccountData">
              {{ exportAccountMutation.isPending.value ? '导出中...' : '导出全部数据' }}
            </button>
          </div>

          <div class="data-card danger app-card">
            <h3>删除账户</h3>
            <p>此操作不可恢复，账户、任务、文档和认证数据都会被永久删除。</p>
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
