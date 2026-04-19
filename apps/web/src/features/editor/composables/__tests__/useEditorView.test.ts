/**
 * useEditorView composable 测试。
 *
 * 通过真实组件挂载来避免 lifecycle warning。
 */
import { mount } from '@vue/test-utils';
import { defineComponent } from 'vue';
import { describe, expect, it, vi } from 'vitest';

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { taskId: 'task-123' } }),
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock('@/features/editor/composables/useEditor', async () => {
  const { ref } = await vi.importActual<typeof import('vue')>('vue');
  return {
    useTaskDocuments: () => ({
      data: ref({ items: [] }),
      isLoading: ref(false),
      refetch: vi.fn(),
    }),
    useDocumentHistory: () => ({
      data: ref({ items: [] }),
      isLoading: ref(false),
      refetch: vi.fn(),
    }),
    useDocumentSnapshot: () => ({
      data: ref(null),
      isLoading: ref(false),
    }),
    useRestoreSnapshotMutation: () => ({ mutateAsync: vi.fn() }),
  };
});

vi.mock('@/features/task/composables/useTasks', async () => {
  const { ref } = await vi.importActual<typeof import('vue')>('vue');
  return {
    useTask: () => ({
      data: ref(null),
      isLoading: ref(false),
      refetch: vi.fn(),
    }),
  };
});

vi.mock('@/features/editor/composables/useAutoSave', () => ({
  useAutoSave: () => ({
    persistDocument: vi.fn(),
    ensureLatestDocumentSaved: vi.fn(() => Promise.resolve(true)),
    handleOnline: vi.fn(),
    handleOffline: vi.fn(),
  }),
}));

vi.mock('@/features/editor/composables/useEditorGeneration', () => ({
  useEditorGeneration: () => ({
    generationProgress: {
      isGenerating: false,
      completed: 0,
      total: 0,
      currentSection: '',
      currentSectionName: null,
      streamingText: '',
      docType: '',
    },
    startGeneration: vi.fn(),
    stopGeneration: vi.fn(),
  }),
}));

vi.mock('@/features/editor/composables/useEditorRewrite', () => ({
  useEditorRewrite: () => ({
    rewriteState: {
      isRewriting: false,
      sectionName: null,
      action: 'rewrite',
      streamingText: '',
    },
    startSectionRewrite: vi.fn(),
  }),
}));

vi.mock('@/features/export/composables/useExport', () => ({
  exportDocx: vi.fn(),
  exportMultipleDocx: vi.fn(),
}));

vi.mock('@/shared/composables/useToast', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  }),
}));

vi.mock('@/shared/api/errors', () => ({
  getErrorDescription: (_err: unknown, fallback: string) => fallback,
}));

async function createView() {
  const { useEditorView } = await import('../useEditorView');
  let view: ReturnType<typeof useEditorView> | null = null;

  const Harness = defineComponent({
    setup() {
      view = useEditorView();
      return () => null;
    },
  });

  const wrapper = mount(Harness);
  return {
    view: view!,
    unmount: () => wrapper.unmount(),
  };
}

describe('useEditorView', () => {
  it('returns all expected properties', async () => {
    const { view, unmount } = await createView();

    expect(view).toHaveProperty('draftDocument');
    expect(view).toHaveProperty('saveState');
    expect(view).toHaveProperty('streamError');
    expect(view).toHaveProperty('sections');
    expect(view).toHaveProperty('currentDocType');

    expect(typeof view.confirmSectionByName).toBe('function');
    expect(typeof view.confirmAll).toBe('function');
    expect(typeof view.updateSectionData).toBe('function');
    expect(typeof view.getSectionData).toBe('function');
    expect(typeof view.getSectionReferences).toBe('function');
    expect(typeof view.toggleSectionCollapse).toBe('function');
    expect(typeof view.toggleAllSections).toBe('function');
    expect(typeof view.scrollToSection).toBe('function');
    expect(typeof view.refreshFromServer).toBe('function');
    expect(typeof view.handleExport).toBe('function');
    expect(typeof view.handleExportAll).toBe('function');
    expect(typeof view.startGeneration).toBe('function');
    expect(typeof view.stopGeneration).toBe('function');
    expect(typeof view.startSectionRewrite).toBe('function');

    unmount();
  });

  it('returns empty/null-safe section helpers when no document loaded', async () => {
    const { view, unmount } = await createView();

    expect(view.getSectionData('objectives')).toBeNull();
    expect(view.getSectionReferences('objectives')).toEqual([]);
    expect(() => view.updateSectionData('objectives', [])).not.toThrow();
    expect(() => view.confirmSectionByName('objectives')).not.toThrow();
    expect(() => view.confirmAll()).not.toThrow();
    expect(view.draftDocument.value).toBeNull();
    expect(view.hasPending.value).toBe(false);
    expect(view.sections.value).toEqual([]);

    unmount();
  });
});
