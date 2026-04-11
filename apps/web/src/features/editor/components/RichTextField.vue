<script setup lang="ts">
import Underline from '@tiptap/extension-underline';
import StarterKit from '@tiptap/starter-kit';
import { EditorContent, useEditor } from '@tiptap/vue-3';
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';

const props = withDefaults(
  defineProps<{
    modelValue: string;
    disabled?: boolean;
    allowSelectionAi?: boolean;
  }>(),
  {
    disabled: false,
    allowSelectionAi: false,
  },
);

const emit = defineEmits<{
  'update:modelValue': [value: string];
  'selection-action': [payload: { action: 'polish' | 'expand'; selectionText: string }];
}>();

const rootElement = ref<HTMLElement | null>(null);
const selectionText = ref('');
const isFocused = ref(false);
const toolbarStyle = ref({ left: '0px', top: '0px' });

type ToolbarEditor = {
  state: {
    selection: {
      from: number;
      to: number;
    };
    doc: {
      textBetween: (from: number, to: number, blockSeparator?: string) => string;
    };
  };
  view: {
    coordsAtPos: (pos: number) => { left: number; right: number; top: number };
  };
};

function updateToolbarPosition(
  currentEditor: ToolbarEditor | null | undefined = editor.value as unknown as ToolbarEditor | undefined,
) {
  if (!currentEditor || !rootElement.value) {
    return;
  }

  const { from, to } = currentEditor.state.selection;
  if (from === to) {
    return;
  }

  const start = currentEditor.view.coordsAtPos(from);
  const end = currentEditor.view.coordsAtPos(to);
  const rootRect = rootElement.value.getBoundingClientRect();
  const centerX = (start.left + end.right) / 2 - rootRect.left;
  const top = Math.min(start.top, end.top) - rootRect.top - 12;

  toolbarStyle.value = {
    left: `${Math.max(20, centerX)}px`,
    top: `${Math.max(8, top)}px`,
  };
}

function syncSelection(currentEditor: ToolbarEditor) {
  const { from, to } = currentEditor.state.selection;
  selectionText.value = from === to ? '' : currentEditor.state.doc.textBetween(from, to, ' ').trim();
  if (from !== to) {
    nextTick(() => updateToolbarPosition());
  }
}

const editor = useEditor({
  extensions: [StarterKit, Underline],
  content: props.modelValue,
  editable: !props.disabled,
  onUpdate: ({ editor: currentEditor }) => {
    emit('update:modelValue', currentEditor.getHTML());
    if (selectionText.value) {
      nextTick(() => updateToolbarPosition(currentEditor));
    }
  },
  onSelectionUpdate: ({ editor: currentEditor }) => {
    syncSelection(currentEditor);
  },
  onFocus: ({ editor: currentEditor }) => {
    isFocused.value = true;
    syncSelection(currentEditor);
  },
  onBlur: () => {
    isFocused.value = false;
  },
});

const showToolbar = computed(
  () => props.allowSelectionAi && !props.disabled && isFocused.value && selectionText.value.length > 0,
);

function emitSelectionAction(action: 'polish' | 'expand') {
  if (!selectionText.value.trim()) {
    return;
  }
  emit('selection-action', { action, selectionText: selectionText.value.trim() });
}

function handleViewportChange() {
  if (showToolbar.value) {
    updateToolbarPosition();
  }
}

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

onMounted(() => {
  if (typeof window === 'undefined') {
    return;
  }
  window.addEventListener('resize', handleViewportChange);
  window.addEventListener('scroll', handleViewportChange, true);
});

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleViewportChange);
    window.removeEventListener('scroll', handleViewportChange, true);
  }
  editor.value?.destroy();
});
</script>

<template>
  <div ref="rootElement" class="rich-editor" :class="{ readonly: disabled }">
    <div v-if="showToolbar" class="floating-toolbar" :style="toolbarStyle" @mousedown.prevent>
      <button class="toolbar-button" type="button" @click="editor?.chain().focus().toggleBold().run()">
        B
      </button>
      <button class="toolbar-button" type="button" @click="editor?.chain().focus().toggleItalic().run()">
        I
      </button>
      <button class="toolbar-button" type="button" @click="editor?.chain().focus().toggleUnderline().run()">
        U
      </button>
      <span class="toolbar-divider" />
      <button class="toolbar-chip" type="button" @click="emitSelectionAction('polish')">AI 润色</button>
      <button class="toolbar-chip" type="button" @click="emitSelectionAction('expand')">AI 扩写</button>
    </div>
    <EditorContent :editor="editor" />
  </div>
</template>
