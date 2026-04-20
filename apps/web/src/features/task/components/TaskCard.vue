<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';

import type { TaskRecord } from '@/features/task/types';

const props = defineProps<{
  task: TaskRecord;
}>();

const emit = defineEmits<{
  open: [];
  export: [];
  duplicate: [];
  delete: [];
}>();

const rootRef = ref<HTMLElement | null>(null);
const menuOpen = ref(false);

const relativeTime = computed(() => {
  const updatedAt = new Date(props.task.updated_at).getTime();
  if (Number.isNaN(updatedAt)) {
    return '刚刚编辑';
  }

  const diff = Math.max(0, Date.now() - updatedAt);
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days >= 30) {
    return `${Math.floor(days / 30)} 月前编辑`;
  }
  if (days >= 1) {
    return `${days} 天前编辑`;
  }
  if (hours >= 1) {
    return `${hours} 小时前编辑`;
  }
  if (minutes >= 1) {
    return `${minutes} 分钟前编辑`;
  }
  return '刚刚编辑';
});

function handleDocumentClick(event: MouseEvent) {
  if (!rootRef.value?.contains(event.target as Node)) {
    menuOpen.value = false;
  }
}

function handleExport(event: MouseEvent) {
  event.stopPropagation();
  menuOpen.value = false;
  emit('export');
}

function handleDuplicate(event: MouseEvent) {
  event.stopPropagation();
  menuOpen.value = false;
  emit('duplicate');
}

function handleDelete(event: MouseEvent) {
  event.stopPropagation();
  menuOpen.value = false;
  emit('delete');
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick);
});
</script>

<template>
  <article
    ref="rootRef"
    class="task-card"
    role="button"
    tabindex="0"
    @click="emit('open')"
    @keydown.enter.prevent="emit('open')"
    @keydown.space.prevent="emit('open')"
  >
    <div class="task-card-icon">📄</div>
    <div class="task-card-body">
      <h3>{{ task.title }}</h3>
      <p>{{ task.subject }} · {{ task.grade }}</p>
      <span>{{ relativeTime }}</span>
    </div>

    <div class="task-card-menu">
      <button
        class="task-card-menu-trigger"
        type="button"
        aria-label="更多操作"
        @click.stop="menuOpen = !menuOpen"
      >
        ⋮
      </button>

      <div v-if="menuOpen" class="task-card-menu-panel app-card">
        <button type="button" @click.stop="emit('open')">继续编辑</button>
        <button type="button" @click.stop="handleExport">导出 Word</button>
        <button type="button" @click.stop="handleDuplicate">复制为新教案</button>
        <div class="task-card-menu-divider" />
        <button class="danger" type="button" @click.stop="handleDelete">删除</button>
      </div>
    </div>
  </article>
</template>
