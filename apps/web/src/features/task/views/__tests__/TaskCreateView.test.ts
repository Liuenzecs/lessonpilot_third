import { mount } from '@vue/test-utils';
import { ref } from 'vue';
import { describe, expect, it, vi } from 'vitest';

import TaskCreateView from '../TaskCreateView.vue';

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
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
  it('uses the launch-desk copy for document type and primary CTA', () => {
    const wrapper = mount(TaskCreateView);

    expect(wrapper.text()).toContain('文档类型');
    expect(wrapper.text()).toContain('个人资料库');
    expect(wrapper.text()).toContain('进入文档桌');
    expect(wrapper.text()).toContain('备课启动台');
  });
});
