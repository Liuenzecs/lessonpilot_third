import { mount, RouterLinkStub } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import LandingView from '../LandingView.vue';

describe('LandingView', () => {
  it('uses the softer draft-first marketing copy', () => {
    const wrapper = mount(LandingView, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          HeroProductPreview: true,
        },
      },
    });

    expect(wrapper.text()).toContain('先整理出完整初稿');
    expect(wrapper.text()).not.toContain('自动生成结构化教案');
  });
});
