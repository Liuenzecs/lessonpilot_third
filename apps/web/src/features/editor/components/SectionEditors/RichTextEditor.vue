<script setup lang="ts">
/**
 * TipTap 富文本编辑器，用于 section 内的长文本编辑（板书设计、教学反思等）。
 * 基于 RichTextField.vue 改造，移除 block 相关逻辑。
 */
import Underline from '@tiptap/extension-underline';
import StarterKit from '@tiptap/starter-kit';
import { EditorContent, useEditor } from '@tiptap/vue-3';
import { onBeforeUnmount, watch } from 'vue';

const props = withDefaults(
  defineProps<{
    modelValue: string;
    disabled?: boolean;
    placeholder?: string;
  }>(),
  {
    disabled: false,
    placeholder: '',
  },
);

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

const editor = useEditor({
  extensions: [StarterKit, Underline],
  content: props.modelValue,
  editable: !props.disabled,
  editorProps: {
    attributes: {
      class: 'rich-text-content',
    },
  },
  onUpdate: ({ editor: currentEditor }) => {
    emit('update:modelValue', currentEditor.getHTML());
  },
});

watch(
  () => props.modelValue,
  (nextValue) => {
    const currentEditor = editor.value;
    if (!currentEditor || nextValue === currentEditor.getHTML()) {
      return;
    }
    currentEditor.commands.setContent(nextValue, false);
  },
);

watch(
  () => props.disabled,
  (disabled) => {
    editor.value?.setEditable(!disabled);
  },
);

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>

<template>
  <div class="rich-text-editor" :class="{ readonly: disabled }">
    <EditorContent :editor="editor" />
    <div v-if="placeholder && !modelValue" class="rich-text-placeholder">
      {{ placeholder }}
    </div>
  </div>
</template>
