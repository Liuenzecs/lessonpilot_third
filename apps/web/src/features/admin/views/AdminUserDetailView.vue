<script setup lang="ts">
import { computed, reactive } from 'vue';
import { useRoute } from 'vue-router';

import { useCreateQuotaAdjustment, useAdminUserDetail } from '@/features/admin/composables/useAdmin';
import StatePanel from '@/shared/components/StatePanel.vue';
import { getAppErrorState, getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';

const route = useRoute();
const toast = useToast();
const userId = computed(() => String(route.params.userId || ''));
const detailQuery = useAdminUserDetail(userId.value);
const createAdjustmentMutation = useCreateQuotaAdjustment(userId.value);

const form = reactive({
  delta: 1,
  reason: '',
});

const errorState = computed(() =>
  detailQuery.error.value
    ? getAppErrorState(detailQuery.error.value, {
        defaultTitle: '用户详情暂时不可用',
        defaultDescription: '请稍后重试，或返回用户列表重新进入。',
      })
    : null,
);

async function submitAdjustment() {
  try {
    await createAdjustmentMutation.mutateAsync({
      delta: Number(form.delta),
      reason: form.reason || undefined,
    });
    toast.success('月度配额调整已保存');
    form.delta = 1;
    form.reason = '';
  } catch (error) {
    toast.error(getErrorDescription(error, '保存配额调整失败，请稍后再试。'));
  }
}
</script>

<template>
  <section class="admin-section">
    <div class="admin-section-head">
      <div>
        <p class="page-eyebrow">用户详情</p>
        <h2>查看方案、最近行为和手动额度调整</h2>
      </div>
      <button class="button ghost" type="button" @click="detailQuery.refetch()">刷新</button>
    </div>

    <StatePanel
      v-if="detailQuery.isLoading.value"
      icon="…"
      eyebrow="用户详情"
      title="正在加载详情"
      description="我们正在读取用户订阅、最近任务和反馈记录。"
      tone="info"
    />

    <StatePanel
      v-else-if="errorState"
      icon="!"
      :eyebrow="errorState.kind"
      :title="errorState.title"
      :description="errorState.description"
      tone="error"
    >
      <template #actions>
        <button class="button primary" type="button" @click="detailQuery.refetch()">重试</button>
      </template>
    </StatePanel>

    <template v-else-if="detailQuery.data.value">
      <div class="admin-detail-grid">
        <article class="admin-detail-card app-card">
          <p class="page-eyebrow">账户信息</p>
          <h3>{{ detailQuery.data.value.user.name }}</h3>
          <p>{{ detailQuery.data.value.user.email }}</p>
          <p>邮箱验证：{{ detailQuery.data.value.user.email_verified ? '已验证' : '未验证' }}</p>
          <p>当前方案：{{ detailQuery.data.value.subscription.plan_label }}</p>
          <p>订阅状态：{{ detailQuery.data.value.subscription.status }}</p>
          <p>
            本月额度：
            <template v-if="detailQuery.data.value.subscription.monthly_task_limit !== null">
              {{ detailQuery.data.value.subscription.tasks_used_this_month }} /
              {{ detailQuery.data.value.subscription.monthly_task_limit }}
            </template>
            <template v-else>无限</template>
          </p>
        </article>

        <article class="admin-detail-card app-card">
          <p class="page-eyebrow">最新支付</p>
          <template v-if="detailQuery.data.value.latest_paid_order">
            <h3>{{ detailQuery.data.value.latest_paid_order.amount_cents / 100 }} 元</h3>
            <p>渠道：{{ detailQuery.data.value.latest_paid_order.channel }}</p>
            <p>周期：{{ detailQuery.data.value.latest_paid_order.billing_cycle }}</p>
            <p>支付时间：{{ new Date(detailQuery.data.value.latest_paid_order.paid_at || '').toLocaleString() }}</p>
          </template>
          <template v-else>
            <h3>暂无已支付订单</h3>
            <p>这个用户还没有产生已支付的专业版订单记录。</p>
          </template>
        </article>
      </div>

      <div class="admin-detail-grid">
        <article class="admin-detail-card app-card">
          <p class="page-eyebrow">最近任务</p>
          <ul class="admin-inline-list">
            <li v-for="task in detailQuery.data.value.recent_tasks" :key="task.id">
              <strong>{{ task.title }}</strong>
              <span>{{ task.subject }} · {{ task.grade }}</span>
            </li>
          </ul>
          <p v-if="!detailQuery.data.value.recent_tasks.length" class="subtitle">暂无最近任务。</p>
        </article>

        <article class="admin-detail-card app-card">
          <p class="page-eyebrow">最近反馈</p>
          <ul class="admin-inline-list">
            <li v-for="feedback in detailQuery.data.value.recent_feedback" :key="feedback.id">
              <strong>{{ feedback.mood }}</strong>
              <span>{{ feedback.message }}</span>
            </li>
          </ul>
          <p v-if="!detailQuery.data.value.recent_feedback.length" class="subtitle">暂无最近反馈。</p>
        </article>
      </div>

      <div class="admin-detail-grid">
        <article class="admin-detail-card app-card">
          <p class="page-eyebrow">手动额度调整</p>
          <div class="admin-adjustment-form">
            <label>
              增减值
              <input v-model.number="form.delta" type="number" min="-100" max="100" step="1" />
            </label>
            <label>
              备注
              <textarea v-model.trim="form.reason" rows="3" placeholder="例如：客服补偿、手动纠偏"></textarea>
            </label>
            <button class="button primary" type="button" @click="submitAdjustment()">保存调整</button>
          </div>
        </article>

        <article class="admin-detail-card app-card">
          <p class="page-eyebrow">调整记录</p>
          <ul class="admin-inline-list">
            <li v-for="entry in detailQuery.data.value.quota_adjustments" :key="entry.id">
              <strong>{{ entry.month_key }} / {{ entry.delta > 0 ? `+${entry.delta}` : entry.delta }}</strong>
              <span>{{ entry.reason || '无备注' }}</span>
            </li>
          </ul>
          <p v-if="!detailQuery.data.value.quota_adjustments.length" class="subtitle">还没有手动调整记录。</p>
        </article>
      </div>
    </template>
  </section>
</template>
