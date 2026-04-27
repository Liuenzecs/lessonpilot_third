import { flushPromises, mount } from '@vue/test-utils';
import { ref } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import PersonalAssetsView from '../PersonalAssetsView.vue';

const mockPreview = vi.hoisted(() => vi.fn());
const mockConfirm = vi.hoisted(() => vi.fn());

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock('@/features/task/composables/useTasks', () => ({
  usePersonalAssets: () => ({
    data: ref([]),
    isLoading: ref(false),
  }),
  usePreviewPersonalAssetMutation: () => ({ mutateAsync: mockPreview, isPending: ref(false) }),
  useConfirmPersonalAssetMutation: () => ({ mutateAsync: mockConfirm, isPending: ref(false) }),
  useDeletePersonalAssetMutation: () => ({ mutateAsync: vi.fn(), isPending: ref(false) }),
}));

vi.mock('@/shared/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn(), info: vi.fn() }),
}));

vi.mock('@/shared/api/errors', () => ({
  getErrorDescription: (_error: unknown, fallback: string) => fallback,
}));

describe('PersonalAssetsView', () => {
  beforeEach(() => {
    mockPreview.mockReset();
    mockConfirm.mockReset();
    mockPreview.mockResolvedValue({
      source_filename: 'spring.pptx',
      file_type: 'pptx',
      title: '春课件',
      subject: '语文',
      grade: '七年级',
      topic: '春',
      asset_type: 'ppt_outline',
      extracted_sections: [{ title: '第 1 页', content: '导入春景图片', section_type: 'ppt_slide' }],
      unmapped_sections: [],
      reuse_suggestions: [{ target: 'teaching_package', label: '作为上课包参考', reason: '可复用问题链' }],
      warnings: [],
    });
    mockConfirm.mockResolvedValue({ id: 'asset-1' });
  });

  it('previews and saves personal material', async () => {
    const wrapper = mount(PersonalAssetsView);
    const input = wrapper.find('input[type="file"]');
    const file = new File(['pptx'], 'spring.pptx', { type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' });
    Object.defineProperty(input.element, 'files', { value: [file] });

    await input.trigger('change');
    await flushPromises();

    expect(wrapper.text()).toContain('PPT 大纲');
    expect(wrapper.text()).toContain('导入春景图片');
    const saveButton = wrapper.findAll('button').find((button) => button.text().includes('保存到资料库'));
    await saveButton?.trigger('click');
    await flushPromises();
    expect(mockConfirm).toHaveBeenCalled();
  });
});
