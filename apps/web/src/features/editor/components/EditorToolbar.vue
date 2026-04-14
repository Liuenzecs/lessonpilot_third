<script setup lang="ts">
/**
 * 编辑器工具栏：全部展开/折叠、确认全部。
 */
defineProps<{
  allCollapsed: boolean;
  hasPending: boolean;
}>();

const emit = defineEmits<{
  'toggle-all': [];
  'confirm-all': [];
}>();
</script>

<template>
  <div class="editor-toolbar">
    <button type="button" class="toolbar-btn" @click="emit('toggle-all')">
      {{ allCollapsed ? '全部展开' : '全部折叠' }}
    </button>
    <button
      v-if="hasPending"
      type="button"
      class="toolbar-btn primary"
      @click="emit('confirm-all')"
    >
      确认全部
    </button>
  </div>
</template>
