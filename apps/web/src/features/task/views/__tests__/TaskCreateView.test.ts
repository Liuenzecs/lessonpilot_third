import { mount } from '@vue/test-utils';
import { nextTick, ref } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import TaskCreateView from '../TaskCreateView.vue';

const routeState = vi.hoisted(() => ({
  query: {} as Record<string, string>,
}));

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => routeState,
}));

vi.mock('@/features/task/composables/useTasks', () => ({
  useCreateTaskMutation: () => ({
    mutateAsync: vi.fn(),
    isPending: ref(false),
  }),
  usePersonalAssetRecommendations: () => ({
    data: ref([]),
    isLoading: ref(false),
  }),
}));

vi.mock('@/shared/composables/useToast', () => ({
  useToast: () => ({
    info: vi.fn(),
    error: vi.fn(),
    success: vi.fn(),
  }),
}));

vi.mock('@/shared/api/client', () => ({
  request: vi.fn(async () => []),
  ApiError: class ApiError extends Error {
    status: number;

    constructor(status = 500) {
      super('api error');
      this.status = status;
    }
  },
}));

describe('TaskCreateView', () => {
  beforeEach(() => {
    routeState.query = {};
  });

  it('uses the launch-desk copy for document type and primary CTA', () => {
    const wrapper = mount(TaskCreateView);

    expect(wrapper.text()).toContain('文档类型');
    expect(wrapper.text()).toContain('个人资料库');
    expect(wrapper.text()).toContain('进入文档桌');
    expect(wrapper.text()).toContain('备课启动台');
    expect(wrapper.text()).toContain('套用试用样例');
    expect(wrapper.text()).toContain('试用验收路径');
  });

  it('prefills the first lesson sample when preset query is present', async () => {
    routeState.query = { preset: 'first-lesson' };
    const wrapper = mount(TaskCreateView);

    await nextTick();

    const topicInput = wrapper.find<HTMLInputElement>('input.create-topic-input');
    const requirementsInput = wrapper.find<HTMLTextAreaElement>('textarea.create-textarea');

    expect(topicInput.element.value).toBe('朱自清《春》 第一课时');
    expect(requirementsInput.element.value).toContain('可提交的公立校教案');
    expect(wrapper.text()).toContain('首份备课样例已填好');
    expect(wrapper.text()).toContain('七年级');
  });
});
