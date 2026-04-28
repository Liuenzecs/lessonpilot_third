import { mount } from '@vue/test-utils';
import { ref } from 'vue';
import { describe, expect, it, vi } from 'vitest';

import SettingsView from '../SettingsView.vue';

const styleUpdate = vi.hoisted(() => vi.fn());

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock('@/app/stores/auth', () => ({
  useAuthStore: () => ({
    setUser: vi.fn(),
    clearSession: vi.fn(),
  }),
}));

vi.mock('@/features/auth/composables/useAuth', () => ({
  useResendVerificationMutation: () => ({
    mutateAsync: vi.fn(),
    isPending: ref(false),
  }),
}));

vi.mock('@/features/settings/composables/useAccount', () => ({
  useAccount: () => ({
    data: ref({
      id: 'u1',
      email: 'teacher@example.com',
      name: 'Teacher',
      email_verified: true,
      email_verified_at: null,
      created_at: '2026-04-28T00:00:00Z',
    }),
    error: ref(null),
    isLoading: ref(false),
    refetch: vi.fn(),
  }),
  useUpdateAccountMutation: () => ({ mutateAsync: vi.fn(), isPending: ref(false) }),
  useChangePasswordMutation: () => ({ mutateAsync: vi.fn(), isPending: ref(false) }),
  useExportAccountMutation: () => ({ mutateAsync: vi.fn(), isPending: ref(false) }),
  useDeleteAccountMutation: () => ({ mutateAsync: vi.fn(), isPending: ref(false) }),
  useStyleProfile: () => ({
    data: ref({
      id: 'style-1',
      enabled: true,
      objective_style: '目标要具体可评价。',
      process_style: '过程要写清追问。',
      school_wording: '',
      activity_preferences: '',
      avoid_phrases: '',
      sample_count: 0,
      created_at: '2026-04-28T00:00:00Z',
      updated_at: '2026-04-28T00:00:00Z',
    }),
    isLoading: ref(false),
  }),
  useUpdateStyleProfileMutation: () => ({
    mutateAsync: styleUpdate,
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

describe('SettingsView style memory', () => {
  it('shows and saves teacher style memory', async () => {
    const wrapper = mount(SettingsView);

    await wrapper.findAll('button').find((button) => button.text() === '风格记忆')?.trigger('click');

    expect(wrapper.text()).toContain('保存你常用的目标写法');
    expect(wrapper.find<HTMLTextAreaElement>('textarea').element.value).toBe('目标要具体可评价。');

    await wrapper.find('textarea').setValue('使用“通过……学生能够……”句式。');
    await wrapper.findAll('button').find((button) => button.text() === '保存风格记忆')?.trigger('click');

    expect(styleUpdate).toHaveBeenCalledWith(
      expect.objectContaining({
        enabled: true,
        objective_style: '使用“通过……学生能够……”句式。',
      }),
    );
  });
});
