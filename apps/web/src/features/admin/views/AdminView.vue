<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import { useAuthStore } from '@/app/stores/auth';
import { request } from '@/shared/api/client';

interface AdminUser {
  id: string;
  email: string;
  name: string;
  role: string;
  is_disabled: boolean;
  email_verified: boolean;
  created_at: string;
  gens_today: number;
  gens_this_month: number;
  cost_this_month: number;
}

interface AdminStats {
  total_users: number;
  active_users_7d: number;
  active_users_30d: number;
  total_generations_today: number;
  total_generations_this_month: number;
  cost_today: number;
  cost_this_month: number;
  budget_status: { status: string; cost_month: number; budget: number; percent: number };
}

const authStore = useAuthStore();

const accessChecked = ref(false);
const hasAccess = ref(false);

const stats = ref<AdminStats | null>(null);
const users = ref<AdminUser[]>([]);
const totalUsers = ref(0);
const page = ref(1);
const limit = 20;
const search = ref('');
const loading = ref(false);
const errorMsg = ref('');
const activeTab = ref<'stats' | 'users'>('stats');

async function checkAccess() {
  try {
    const data = await request<AdminStats>('/api/v1/admin/stats');
    stats.value = data;
    hasAccess.value = true;
  } catch (e: any) {
    if (e?.status === 403) {
      hasAccess.value = false;
    } else {
      errorMsg.value = e?.message || '加载失败';
      hasAccess.value = true; // still show the panel so user can see the error
    }
  }
  accessChecked.value = true;
}

async function fetchStats() {
  loading.value = true;
  errorMsg.value = '';
  try {
    stats.value = await request<AdminStats>('/api/v1/admin/stats');
    hasAccess.value = true;
  } catch (e: any) {
    if (e?.status === 403) hasAccess.value = false;
    else errorMsg.value = e?.message || '加载统计数据失败';
  }
  loading.value = false;
}

async function fetchUsers() {
  loading.value = true;
  errorMsg.value = '';
  try {
    const qs = new URLSearchParams({ page: String(page.value), limit: String(limit) });
    if (search.value) qs.set('search', search.value);
    const res = await request<{ users: AdminUser[]; total: number }>(
      `/api/v1/admin/users?${qs.toString()}`,
    );
    users.value = res.users;
    totalUsers.value = res.total;
  } catch (e: any) {
    errorMsg.value = e?.message || '加载用户列表失败';
  }
  loading.value = false;
}

async function disableUser(userId: string) {
  await request(`/api/v1/admin/users/${encodeURIComponent(userId)}/disable`, { method: 'POST', body: JSON.stringify({ reason: '' }) });
  fetchUsers();
}

async function enableUser(userId: string) {
  await request(`/api/v1/admin/users/${encodeURIComponent(userId)}/enable`, { method: 'POST' });
  fetchUsers();
}

checkAccess();

watch(activeTab, (tab) => {
  if (!hasAccess.value) return;
  if (tab === 'stats' && !stats.value) fetchStats();
  else if (tab === 'users') fetchUsers();
});

watch(page, () => fetchUsers());

const totalPages = computed(() => Math.max(1, Math.ceil(totalUsers.value / limit)));

function onSearch() {
  page.value = 1;
  fetchUsers();
}
</script>

<template>
  <div class="admin-page">
    <div v-if="!accessChecked" class="admin-loading app-card">验证权限中...</div>

    <div v-else-if="!hasAccess" class="admin-forbidden app-card">
      <h2>无权限</h2>
      <p>你没有管理后台的访问权限。如需管理员权限，请联系系统管理员。</p>
    </div>

    <template v-else>
      <div class="admin-hero">
        <h1>管理后台</h1>
      </div>

      <div class="admin-tabs">
        <button :class="{ active: activeTab === 'stats' }" @click="activeTab = 'stats'">统计面板</button>
        <button :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">用户管理</button>
      </div>

      <div v-if="loading" class="admin-loading app-card">加载中...</div>
      <div v-else-if="errorMsg" class="admin-error app-card">{{ errorMsg }}</div>

      <!-- Stats Panel -->
      <template v-else-if="activeTab === 'stats' && stats">
        <section class="admin-grid">
          <div class="stat-card app-card">
            <span class="stat-label">总用户数</span>
            <span class="stat-value">{{ stats.total_users }}</span>
          </div>
          <div class="stat-card app-card">
            <span class="stat-label">7 日活跃</span>
            <span class="stat-value">{{ stats.active_users_7d }}</span>
          </div>
          <div class="stat-card app-card">
            <span class="stat-label">30 日活跃</span>
            <span class="stat-value">{{ stats.active_users_30d }}</span>
          </div>
          <div class="stat-card app-card">
            <span class="stat-label">今日生成</span>
            <span class="stat-value">{{ stats.total_generations_today }}</span>
          </div>
          <div class="stat-card app-card">
            <span class="stat-label">本月生成</span>
            <span class="stat-value">{{ stats.total_generations_this_month }}</span>
          </div>
          <div class="stat-card app-card">
            <span class="stat-label">今日成本</span>
            <span class="stat-value">¥{{ stats.cost_today.toFixed(2) }}</span>
          </div>
          <div class="stat-card app-card">
            <span class="stat-label">本月成本</span>
            <span class="stat-value">¥{{ stats.cost_this_month.toFixed(2) }}</span>
          </div>
          <div class="stat-card app-card" :class="{ 'budget-critical': stats.budget_status.status === 'critical', 'budget-warning': stats.budget_status.status === 'warning' }">
            <span class="stat-label">预算状态</span>
            <span class="stat-value">
              <template v-if="stats.budget_status.budget > 0">
                {{ stats.budget_status.percent }}%
              </template>
              <template v-else>未设置</template>
            </span>
            <span class="stat-sub">¥{{ stats.budget_status.cost_month.toFixed(2) }} / ¥{{ stats.budget_status.budget.toFixed(0) }}</span>
          </div>
        </section>
      </template>

      <!-- Users Panel -->
      <template v-else-if="activeTab === 'users'">
        <div class="admin-search">
          <input v-model.trim="search" type="text" placeholder="搜索姓名或邮箱..." @keyup.enter="onSearch" />
          <button class="button primary" @click="onSearch">搜索</button>
        </div>

        <div class="admin-table-wrap app-card">
          <table class="admin-table">
            <thead>
              <tr>
                <th>姓名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>状态</th>
                <th>今日生成</th>
                <th>本月成本</th>
                <th>注册时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id" :class="{ disabled: u.is_disabled }">
                <td>{{ u.name }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.role === 'admin' ? '管理员' : '教师' }}</td>
                <td>
                  <span :class="u.is_disabled ? 'status-disabled' : 'status-active'">
                    {{ u.is_disabled ? '已禁用' : '正常' }}
                  </span>
                </td>
                <td>{{ u.gens_today }}</td>
                <td>¥{{ u.cost_this_month.toFixed(2) }}</td>
                <td>{{ new Date(u.created_at).toLocaleDateString() }}</td>
                <td>
                  <button
                    v-if="u.is_disabled"
                    class="button ghost small"
                    @click="enableUser(u.id)"
                  >启用</button>
                  <button
                    v-else
                    class="button danger small"
                    @click="disableUser(u.id)"
                  >禁用</button>
                </td>
              </tr>
              <tr v-if="users.length === 0">
                <td colspan="8" class="admin-empty">暂无用户</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="totalPages > 1" class="admin-pagination">
          <button class="button ghost" :disabled="page <= 1" @click="page--">上一页</button>
          <span>{{ page }} / {{ totalPages }}</span>
          <button class="button ghost" :disabled="page >= totalPages" @click="page++">下一页</button>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.admin-page { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }
.admin-hero { margin-bottom: 24px; }
.admin-hero h1 { font-size: 24px; }

.admin-tabs {
  display: flex; gap: 8px; margin-bottom: 24px;
}
.admin-tabs button {
  padding: 8px 20px; border: 1px solid var(--border); border-radius: 8px;
  background: var(--surface); font-size: 14px; cursor: pointer;
}
.admin-tabs button.active { border-color: var(--primary); background: rgba(45,104,237,0.08); color: var(--primary); font-weight: 600; }

.admin-forbidden { padding: 48px; text-align: center; }
.admin-forbidden h2 { color: var(--danger); margin-bottom: 8px; }

.admin-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.stat-card { padding: 20px; display: flex; flex-direction: column; gap: 4px; }
.stat-label { font-size: 13px; color: var(--muted); }
.stat-value { font-size: 28px; font-weight: 700; }
.stat-sub { font-size: 12px; color: var(--muted); }
.budget-warning { border-color: var(--warning, #f59e0b); }
.budget-critical { border-color: var(--danger, #ef4444); }

.admin-loading, .admin-error { padding: 32px; text-align: center; }
.admin-error { color: var(--danger); }

.admin-search { display: flex; gap: 8px; margin-bottom: 16px; }
.admin-search input { flex: 1; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; }

.admin-table-wrap { padding: 0; overflow-x: auto; }
.admin-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.admin-table th { text-align: left; padding: 10px 12px; border-bottom: 2px solid var(--border); color: var(--muted); font-size: 12px; }
.admin-table td { padding: 10px 12px; border-bottom: 1px solid var(--border); }
.admin-table tr.disabled td { opacity: 0.5; }
.admin-empty { text-align: center; color: var(--muted); padding: 32px !important; }

.status-active { color: var(--success); }
.status-disabled { color: var(--danger); }

.button.small { padding: 4px 12px; font-size: 12px; }

.admin-pagination { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 16px; }
</style>
