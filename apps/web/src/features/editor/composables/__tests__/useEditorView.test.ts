/**
 * useEditorView composable 测试。
 *
 * 测试核心的状态管理和 section 操作逻辑，
 * mock 掉 Vue Router、TanStack Query、useToast 等外部依赖。
 */
import { describe, expect, it, vi } from 'vitest';

// ---------------------------------------------------------------------------
// Mocks — 必须在 import 被测模块之前声明
// ---------------------------------------------------------------------------

// Vue Router
vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { taskId: 'task-123' } }),
  useRouter: () => ({ push: vi.fn() }),
}));

// TanStack Query — 返回空响应
vi.mock('@/features/editor/composables/useEditor', () => ({
  useTaskDocuments: () => ({
    data: { value: { items: [] } },
    isLoading: { value: false },
    refetch: vi.fn(),
  }),
  useDocumentHistory: () => ({ data: { value: null }, refetch: vi.fn() }),
  useDocumentSnapshot: () => ({ data: { value: null } }),
  useRestoreSnapshotMutation: () => ({ mutateAsync: vi.fn() }),
}));

vi.mock('@/features/task/composables/useTasks', () => ({
  useTask: () => ({
    data: { value: null },
    isLoading: { value: false },
    refetch: vi.fn(),
  }),
}));

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
    generationProgress: { value: null },
    startGeneration: vi.fn(),
    stopGeneration: vi.fn(),
  }),
}));

vi.mock('@/features/editor/composables/useEditorRewrite', () => ({
  useEditorRewrite: () => ({
    rewriteState: { value: 'idle' },
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
  }),
}));

vi.mock('@/shared/api/errors', () => ({
  getErrorDescription: (_err: unknown, fallback: string) => fallback,
}));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('useEditorView', () => {
  async function createView() {
    const { useEditorView } = await import('../useEditorView');
    return useEditorView();
  }

  it('returns all expected properties', async () => {
    const view = await createView();

    // 检查核心 ref 存在
    expect(view).toHaveProperty('draftDocument');
    expect(view).toHaveProperty('saveState');
    expect(view).toHaveProperty('streamError');
    expect(view).toHaveProperty('sections');
    expect(view).toHaveProperty('currentDocType');

    // 检查核心方法存在
    expect(typeof view.confirmSectionByName).toBe('function');
    expect(typeof view.confirmAll).toBe('function');
    expect(typeof view.updateSectionData).toBe('function');
    expect(typeof view.getSectionData).toBe('function');
    expect(typeof view.toggleSectionCollapse).toBe('function');
    expect(typeof view.toggleAllSections).toBe('function');
    expect(typeof view.scrollToSection).toBe('function');
    expect(typeof view.refreshFromServer).toBe('function');
    expect(typeof view.handleExport).toBe('function');
    expect(typeof view.handleExportAll).toBe('function');
    expect(typeof view.startGeneration).toBe('function');
    expect(typeof view.stopGeneration).toBe('function');
    expect(typeof view.startSectionRewrite).toBe('function');
  });

  it('getSectionData returns null when no document loaded', async () => {
    const view = await createView();
    expect(view.getSectionData('objectives')).toBeNull();
  });

  it('updateSectionData does nothing when no document loaded', async () => {
    const view = await createView();
    expect(() => view.updateSectionData('objectives', [])).not.toThrow();
    expect(view.draftDocument.value).toBeNull();
  });

  it('confirmSectionByName does nothing when no document loaded', async () => {
    const view = await createView();
    expect(() => view.confirmSectionByName('objectives')).not.toThrow();
    expect(view.draftDocument.value).toBeNull();
  });

  it('confirmAll does nothing when no document loaded', async () => {
    const view = await createView();
    expect(() => view.confirmAll()).not.toThrow();
    expect(view.draftDocument.value).toBeNull();
  });

  it('has pending=false when no document loaded', async () => {
    const view = await createView();
    expect(view.hasPending.value).toBe(false);
  });

  it('sections is empty when no document loaded', async () => {
    const view = await createView();
    expect(view.sections.value).toEqual([]);
  });
});
