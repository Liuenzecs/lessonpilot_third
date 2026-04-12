<script setup lang="ts">
import { computed, ref } from 'vue';
import { RouterLink } from 'vue-router';

import { useAdminUsers } from '@/features/admin/composables/useAdmin';
import StatePanel from '@/shared/components/StatePanel.vue';
import { getAppErrorState } from '@/shared/api/errors';

const search = ref('');
const plan = ref('');
const status = ref('');

const usersQuery = useAdminUsers({ query: search, plan, status });
const errorState = computed(() =>
  usersQuery.error.value
    ? getAppErrorState(usersQuery.error.value, {
        defaultTitle: '用户列表暂时不可用',
        defaultDescription: '请稍后重试，或检查后端是否正常运行。',
      })
    : null,
);
</script>

<template>
  <section class="admin-section">
    <div class="admin-section-head">
      <div>
        <p class="page-eyebrow">用户管理</p>
        <h2>查找用户、筛选方案、进入详情</h2>
      </div>
      <button class="button ghost" type="button" @click="usersQuery.refetch()">刷新</button>
    </div>

    <div class="admin-filters app-card">
      <input v-model.trim="search" class="admin-search" type="search" placeholder="搜索邮箱或姓名" />
      <select v-model="plan">
        <option value="">全部方案</option>
        <option value="free">免费版</option>
        <option value="professional">专业版</option>
      </select>
      <select v-model="status">
        <option value="">全部状态</option>
        <option value="free">免费</option>
        <option value="trialing">试用中</option>
        <option value="active">有效</option>
        <option value="expired">已到期</option>
      </select>
    </div>

    <StatePanel
      v-if="usersQuery.isLoading.value"
      icon="…"
      eyebrow="用户列表"
      title="正在加载用户"
      description="我们正在拉取账户、订阅和额度摘要。"
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
        <button class="button primary" type="button" @click="usersQuery.refetch()">重试</button>
      </template>
    </StatePanel>

    <StatePanel
      v-else-if="!usersQuery.data.value?.items.length"
      icon="·"
      eyebrow="用户列表"
      title="没有找到匹配用户"
      description="可以调整搜索词、方案或状态筛选后再试一次。"
      tone="empty"
    />

    <div v-else class="admin-table app-card">
      <div class="admin-table-head">
        <span>用户</span>
        <span>方案</span>
        <span>状态</span>
        <span>本月额度</span>
        <span>操作</span>
      </div>

      <div v-for="item in usersQuery.data.value.items" :key="item.user.id" class="admin-table-row">
        <div>
          <strong>{{ item.user.name }}</strong>
          <p>{{ item.user.email }}</p>
        </div>
        <span>{{ item.subscription.plan_label }}</span>
        <span>{{ item.subscription.status }}</span>
        <span>
          <template v-if="item.subscription.monthly_task_limit !== null">
            {{ item.subscription.tasks_used_this_month }} / {{ item.subscription.monthly_task_limit }}
          </template>
          <template v-else>无限</template>
        </span>
        <RouterLink class="button ghost" :to="{ name: 'admin-user-detail', params: { userId: item.user.id } }">
          查看详情
        </RouterLink>
      </div>
    </div>
  </section>
</template>
