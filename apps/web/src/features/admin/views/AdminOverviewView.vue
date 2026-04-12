<script setup lang="ts">
import { computed } from 'vue';

import { useAdminOverview } from '@/features/admin/composables/useAdmin';
import StatePanel from '@/shared/components/StatePanel.vue';
import { getAppErrorState } from '@/shared/api/errors';

const overviewQuery = useAdminOverview();

const last7 = computed(() => overviewQuery.data.value?.last_7_days ?? []);
const last30 = computed(() => overviewQuery.data.value?.last_30_days ?? []);
const errorState = computed(() =>
  overviewQuery.error.value
    ? getAppErrorState(overviewQuery.error.value, {
        defaultTitle: '运营概览暂时不可用',
        defaultDescription: '请稍后重试，或检查管理员权限是否配置正确。',
      })
    : null,
);
</script>

<template>
  <section class="admin-section">
    <div class="admin-section-head">
      <div>
        <p class="page-eyebrow">近 7 / 30 天</p>
        <h2>运营概览</h2>
      </div>
      <button class="button ghost" type="button" @click="overviewQuery.refetch()">刷新</button>
    </div>

    <StatePanel
      v-if="overviewQuery.isLoading.value"
      icon="…"
      eyebrow="数据加载中"
      title="正在汇总运营指标"
      description="页面访问、注册、试用和支付数据很快就会回来。"
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
        <button class="button primary" type="button" @click="overviewQuery.refetch()">重试</button>
      </template>
    </StatePanel>

    <template v-else>
      <div class="admin-metric-section">
        <h3>近 7 天</h3>
        <div class="admin-metric-grid">
          <article v-for="metric in last7" :key="`seven-${metric.key}`" class="admin-metric-card app-card">
            <p>{{ metric.label }}</p>
            <strong>{{ metric.value }}</strong>
          </article>
        </div>
      </div>

      <div class="admin-metric-section">
        <h3>近 30 天</h3>
        <div class="admin-metric-grid">
          <article v-for="metric in last30" :key="`thirty-${metric.key}`" class="admin-metric-card app-card">
            <p>{{ metric.label }}</p>
            <strong>{{ metric.value }}</strong>
          </article>
        </div>
      </div>
    </template>
  </section>
</template>
