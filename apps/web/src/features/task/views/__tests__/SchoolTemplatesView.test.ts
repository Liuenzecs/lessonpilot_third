import { flushPromises, mount } from '@vue/test-utils';
import { ref } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import SchoolTemplatesView from '../SchoolTemplatesView.vue';

const mockPreview = vi.hoisted(() => vi.fn());
const mockConfirm = vi.hoisted(() => vi.fn());
const mockDelete = vi.hoisted(() => vi.fn());

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock('@/features/task/composables/useTasks', () => ({
  useSchoolTemplates: () => ({
    data: ref([{ id: 'tpl-1', name: '本校模板', subject: '语文', grade: '七年级' }]),
    isLoading: ref(false),
  }),
  usePreviewSchoolTemplateMutation: () => ({ mutateAsync: mockPreview, isPending: ref(false) }),
  useConfirmSchoolTemplateMutation: () => ({ mutateAsync: mockConfirm, isPending: ref(false) }),
  useDeleteSchoolTemplateMutation: () => ({ mutateAsync: mockDelete, isPending: ref(false) }),
}));

vi.mock('@/shared/composables/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn(), info: vi.fn() }),
}));

vi.mock('@/shared/api/errors', () => ({
  getErrorDescription: (_error: unknown, fallback: string) => fallback,
}));

describe('SchoolTemplatesView', () => {
  beforeEach(() => {
    mockPreview.mockReset();
    mockConfirm.mockReset();
    mockPreview.mockResolvedValue({
      source_filename: 'template.docx',
      name: '学校模板',
      subject: '语文',
      grade: '七年级',
      template_type: 'lesson_plan',
      field_mappings: [{ template_label: '课题', content_field: 'header.title', confidence: 0.9, location: 'table' }],
      section_order: ['objectives', 'teaching_process'],
      table_layouts: [{ name: 'teaching_process', columns: ['教学环节', '教师活动'], field_mappings: [] }],
      blank_areas: ['教学反思'],
      unsupported_items: [],
      warnings: [],
    });
    mockConfirm.mockResolvedValue({ id: 'tpl-2' });
  });

  it('previews and saves a school template', async () => {
    const wrapper = mount(SchoolTemplatesView);
    const input = wrapper.find('input[type="file"]');
    const file = new File(['docx'], 'template.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    Object.defineProperty(input.element, 'files', { value: [file] });

    await input.trigger('change');
    await flushPromises();

    expect(wrapper.text()).toContain('字段映射');
    const saveButton = wrapper.findAll('button').find((button) => button.text().includes('保存为个人模板'));
    await saveButton?.trigger('click');
    await flushPromises();
    expect(mockConfirm).toHaveBeenCalled();
  });
});
