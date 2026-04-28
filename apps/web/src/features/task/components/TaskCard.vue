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

const documentTypeLabel = computed(() => {
  if (props.task.lesson_type === 'both') return '教案 + 学案';
  if (props.task.lesson_type === 'study_guide') return '学案';
  return '教案';
});

const nextAction = computed(() => {
  if (props.task.status === 'completed') return '可导出';
  if (props.task.status === 'generating') return '生成中';
  return '继续确认';
});

const statusTone = computed(() => {
  if (props.task.status === 'completed') return 'ready';
  if (props.task.status === 'generating') return 'working';
  return 'pending';
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
    <div class="task-card-main">
      <div class="task-card-docmark">文档</div>
      <div class="task-card-body">
        <div class="task-card-meta-row">
          <span>{{ documentTypeLabel }}</span>
          <span>{{ task.subject }} · {{ task.grade }}</span>
        </div>
        <h3>{{ task.title }}</h3>
        <p>{{ task.topic }}</p>
      </div>
    </div>

    <div class="task-card-foot">
      <span class="task-next-action" :class="statusTone">{{ nextAction }}</span>
      <span>{{ relativeTime }}</span>
    </div>

    <div class="task-card-menu" @click.stop>
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
