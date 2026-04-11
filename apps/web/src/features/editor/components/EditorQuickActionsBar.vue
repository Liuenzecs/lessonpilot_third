<script setup lang="ts">
defineProps<{
  currentSectionTitle: string;
  appendOpen: boolean;
  appendInstruction: string;
  appendLoading: boolean;
  disabled: boolean;
}>();

defineEmits<{
  'add-paragraph': [];
  'add-exercise': [];
  'toggle-append': [];
  'update:appendInstruction': [value: string];
  'submit-append': [];
  'cancel-append': [];
}>();
</script>

<template>
  <div class="editor-quick-actions app-card">
    <div class="editor-quick-actions-row">
      <button class="button secondary" type="button" :disabled="disabled" @click="$emit('add-paragraph')">
        + 添加段落
      </button>
      <button class="button secondary" type="button" :disabled="disabled" @click="$emit('toggle-append')">
        AI 补充内容
      </button>
      <button class="button secondary" type="button" :disabled="disabled" @click="$emit('add-exercise')">
        添加练习
      </button>
      <div class="editor-quick-actions-hint">
        当前落点：{{ currentSectionTitle || '未定位章节' }}
      </div>
    </div>

    <div v-if="appendOpen" class="append-composer">
      <input
        :value="appendInstruction"
        type="text"
        placeholder="例如：补一个更自然的导入活动，突出配方法的应用场景。"
        @input="$emit('update:appendInstruction', ($event.target as HTMLInputElement).value)"
      />

      <div class="button-row">
        <button
          class="button primary"
          type="button"
          :disabled="appendLoading || !appendInstruction.trim() || disabled"
          @click="$emit('submit-append')"
        >
          {{ appendLoading ? '生成中...' : '生成补充内容' }}
        </button>
        <button class="button ghost" type="button" :disabled="appendLoading" @click="$emit('cancel-append')">
          取消
        </button>
      </div>
    </div>
  </div>
</template>
