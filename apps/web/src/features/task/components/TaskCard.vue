<script setup lang="ts">
import type { TaskRecord } from '@/features/task/types';

defineProps<{
  task: TaskRecord;
}>();

defineEmits<{
  open: [];
  delete: [];
}>();
</script>

<template>
  <div class="task-card app-card">
    <div>
      <h3>{{ task.title }}</h3>
      <div class="task-meta">{{ task.subject }} · {{ task.grade }}</div>
    </div>
    <div class="task-meta">课题：{{ task.topic }}</div>
    <div class="task-meta">状态：{{ task.status }}</div>
    <div class="button-row">
      <button class="button primary" type="button" @click="$emit('open')">打开编辑</button>
      <button class="button danger" type="button" @click="$emit('delete')">删除</button>
    </div>
  </div>
</template>
