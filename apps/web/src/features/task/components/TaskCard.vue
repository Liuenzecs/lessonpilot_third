<script setup lang="ts">
import { computed } from 'vue';

import type { TaskRecord } from '@/features/task/types';

const props = defineProps<{
  task: TaskRecord;
}>();

const emit = defineEmits<{
  open: [];
  delete: [];
}>();

const relativeTime = computed(() => {
  const updatedAt = new Date(props.task.updated_at).getTime();
  if (Number.isNaN(updatedAt)) {
    return '刚刚更新';
  }

  const diff = Math.max(0, Date.now() - updatedAt);
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days >= 30) {
    return `${Math.floor(days / 30)}个月前`;
  }
  if (days >= 1) {
    return `${days}天前`;
  }
  if (hours >= 1) {
    return `${hours}小时前`;
  }
  if (minutes >= 1) {
    return `${minutes}分钟前`;
  }
  return '刚刚更新';
});

function openCard() {
  emit('open');
}

function removeTask(event: MouseEvent) {
  event.stopPropagation();
  emit('delete');
}
</script>

<template>
  <article
    class="workspace-task-card app-card"
    role="button"
    tabindex="0"
    @click="openCard"
    @keydown.enter.prevent="openCard"
    @keydown.space.prevent="openCard"
  >
    <div class="workspace-task-card-head">
      <div class="workspace-task-card-tag">{{ task.subject }} · {{ task.grade }}</div>
      <button class="workspace-card-delete" type="button" aria-label="删除教案" @click="removeTask">
        删除
      </button>
    </div>

    <div class="workspace-task-card-body">
      <h3 class="workspace-task-card-title">{{ task.title }}</h3>
      <p class="workspace-task-card-topic">{{ task.topic }}</p>
    </div>

    <div class="workspace-task-card-foot">
      <span>{{ relativeTime }}</span>
      <span class="workspace-task-card-link">继续编辑</span>
    </div>
  </article>
</template>
