<script setup lang="ts">
import StarterKit from '@tiptap/starter-kit';
import { EditorContent, useEditor } from '@tiptap/vue-3';
import { onBeforeUnmount, watch } from 'vue';

const props = defineProps<{
  modelValue: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

const editor = useEditor({
  extensions: [StarterKit],
  content: props.modelValue,
  editable: !props.disabled,
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
  <div class="rich-editor">
    <EditorContent :editor="editor" />
  </div>
</template>

