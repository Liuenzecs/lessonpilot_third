<script setup lang="ts">
/**
 * Section 级 AI 操作按钮。
 * 下拉菜单：重写 / 扩写 / 精简，可选自定义指令。
 */
import { ref } from 'vue';

defineProps<{
  disabled?: boolean;
}>();

const emit = defineEmits<{
  action: [payload: { action: 'rewrite' | 'expand' | 'simplify'; instruction: string }];
}>();

const showMenu = ref(false);
const showInstruction = ref(false);
const instruction = ref('');
let closeTimer: ReturnType<typeof setTimeout> | null = null;

function trigger(action: 'rewrite' | 'expand' | 'simplify') {
  emit('action', { action, instruction: instruction.value.trim() });
  showMenu.value = false;
  showInstruction.value = false;
  instruction.value = '';
}

function toggleMenu() {
  showMenu.value = !showMenu.value;
  showInstruction.value = false;
}

function scheduleClose() {
  closeTimer = setTimeout(() => {
    showMenu.value = false;
    showInstruction.value = false;
  }, 150);
}

function cancelClose() {
  if (closeTimer) {
    clearTimeout(closeTimer);
    closeTimer = null;
  }
}
</script>

<template>
  <div class="section-ai-actions" @mouseleave="scheduleClose" @mouseenter="cancelClose">
    <button
      type="button"
      class="ai-trigger-btn"
      :disabled="disabled"
      title="AI 操作"
      @click="toggleMenu"
    >
      AI
    </button>
    <div v-if="showMenu" class="ai-menu">
      <button type="button" class="ai-menu-item" @click="trigger('rewrite')">
        重写
      </button>
      <button type="button" class="ai-menu-item" @click="trigger('expand')">
        扩写
      </button>
      <button type="button" class="ai-menu-item" @click="trigger('simplify')">
        精简
      </button>
      <div class="ai-menu-divider" />
      <button
        type="button"
        class="ai-menu-item"
        @click="showInstruction = !showInstruction"
      >
        自定义指令...
      </button>
      <div v-if="showInstruction" class="ai-instruction-row">
        <input
          v-model="instruction"
          type="text"
          class="ai-instruction-input"
          placeholder="如：加入更多互动环节"
          @keydown.enter="trigger('rewrite')"
        />
        <button
          type="button"
          class="ai-instruction-go"
          @click="trigger('rewrite')"
        >
          执行
        </button>
      </div>
    </div>
  </div>
</template>
