import { flushPromises, mount } from '@vue/test-utils';
import { ref } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import LessonPlanImportView from '../LessonPlanImportView.vue';

const mockPush = vi.hoisted(() => vi.fn());
const mockPreview = vi.hoisted(() => vi.fn());
const mockConfirm = vi.hoisted(() => vi.fn());

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}));

vi.mock('@/features/task/composables/useTasks', () => ({
  usePreviewLessonPlanImportMutation: () => ({
    mutateAsync: mockPreview,
    isPending: ref(false),
  }),
  useConfirmLessonPlanImportMutation: () => ({
    mutateAsync: mockConfirm,
    isPending: ref(false),
  }),
}));

vi.mock('@/shared/composables/useToast', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  }),
}));

vi.mock('@/shared/api/errors', () => ({
  getErrorDescription: (_error: unknown, fallback: string) => fallback,
}));

const previewPayload = {
  source_filename: 'spring.docx',
  metadata: {
    title: '《春》教案',
    subject: '语文',
    grade: '七年级',
    topic: '春',
    class_hour: 1,
    lesson_category: 'new',
    scene: 'public_school',
  },
  content: {
    doc_type: 'lesson_plan',
    header: {
      title: '《春》教案',
      subject: '语文',
      grade: '七年级',
      classHour: 1,
      lessonCategory: 'new',
      teacher: '',
    },
    objectives: [{ dimension: 'knowledge', content: '朗读课文，感受春天景物特点。' }],
    objectives_status: 'pending',
    key_points: { keyPoints: ['品味语言'], difficulties: ['理解情景交融'] },
    key_points_status: 'pending',
    preparation: ['多媒体课件'],
    preparation_status: 'pending',
    teaching_process: [
      {
        phase: '导入新课',
        duration: 5,
        teacher_activity: '展示春景图片。',
        student_activity: '观察并交流。',
        design_intent: '激发兴趣。',
        status: 'pending',
      },
    ],
    teaching_process_status: 'pending',
    board_design: '春：盼春、绘春、赞春',
    board_design_status: 'pending',
    reflection: '课后填写。',
    reflection_status: 'pending',
    section_references: {},
  },
  mapped_sections: ['objectives', 'key_points', 'teaching_process', 'board_design', 'reflection'],
  unmapped_sections: [{ title: null, content: '课堂亮点：朗读节奏要轻快。' }],
  warnings: [{ severity: 'warning', section: null, message: '有 1 段内容未能确定归属，请在预览中检查。' }],
};

describe('LessonPlanImportView', () => {
  beforeEach(() => {
    mockPush.mockReset();
    mockPreview.mockReset();
    mockConfirm.mockReset();
    mockPreview.mockResolvedValue(previewPayload);
    mockConfirm.mockResolvedValue({ task: { id: 'task-1' }, document: { id: 'doc-1' } });
  });

  it('previews a docx import and confirms into the editor', async () => {
    const wrapper = mount(LessonPlanImportView);
    const input = wrapper.find('input[type="file"]');
    const file = new File(['docx'], 'spring.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    });
    Object.defineProperty(input.element, 'files', { value: [file] });

    await input.trigger('change');
    await flushPromises();

    expect(mockPreview).toHaveBeenCalledWith(file);
    expect(wrapper.text()).toContain('识别结果');
    expect(wrapper.text()).toContain('教学目标');
    expect(wrapper.text()).toContain('未识别内容');

    const confirmButton = wrapper.findAll('button').find((button) => button.text().includes('确认导入'));
    await confirmButton?.trigger('click');
    await flushPromises();

    expect(mockConfirm).toHaveBeenCalled();
    expect(mockPush).toHaveBeenCalledWith({ name: 'editor', params: { taskId: 'task-1' } });
  });
});
