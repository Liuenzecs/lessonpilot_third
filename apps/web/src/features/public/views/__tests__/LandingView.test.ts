import { mount, RouterLinkStub } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import LandingView from '../LandingView.vue';

describe('LandingView', () => {
  it('uses the document-desk migration copy', () => {
    const wrapper = mount(LandingView, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
          HeroProductPreview: true,
        },
      },
    });

    expect(wrapper.text()).toContain('教案能交，也能上课');
    expect(wrapper.text()).toContain('试做一份教案');
    expect(wrapper.text()).not.toContain('自动生成结构化教案');
  });
});
