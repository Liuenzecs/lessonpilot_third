<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router';
import { computed } from 'vue';

import { useAdminGuard } from '@/features/admin/composables/useAdmin';
import StatePanel from '@/shared/components/StatePanel.vue';

import '@/features/admin/styles/admin.css';

const route = useRoute();
const { isAdmin } = useAdminGuard();
const isUsersRoute = computed(() => String(route.name || '').startsWith('admin-user'));
</script>

<template>
  <div class="admin-shell">
    <template v-if="isAdmin">
      <header class="admin-topbar app-card">
        <div>
          <p class="page-eyebrow">管理员后台</p>
          <h1>LessonPilot Admin</h1>
        </div>
        <div class="button-row">
          <RouterLink class="button ghost" :to="{ name: 'tasks' }">返回备课台</RouterLink>
        </div>
      </header>

      <div class="admin-body">
        <aside class="admin-sidebar app-card">
          <RouterLink :class="{ active: route.name === 'admin-overview' }" :to="{ name: 'admin-overview' }">
            运营概览
          </RouterLink>
          <RouterLink :class="{ active: isUsersRoute }" :to="{ name: 'admin-users' }">
            用户管理
          </RouterLink>
        </aside>

        <main class="admin-content">
          <RouterView />
        </main>
      </div>
    </template>

    <StatePanel
      v-else
      icon="!"
      eyebrow="管理后台"
      title="你没有访问管理后台的权限"
      description="当前账户不在管理员邮箱白名单中。如需查看运营数据，请联系系统管理员添加权限。"
      tone="error"
    >
      <template #actions>
        <RouterLink class="button primary" :to="{ name: 'tasks' }">返回备课台</RouterLink>
      </template>
    </StatePanel>
  </div>
</template>
