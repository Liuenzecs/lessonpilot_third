import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import CitationTooltip from '../CitationTooltip.vue';

describe('CitationTooltip', () => {
  it('labels personal asset references separately from public knowledge', async () => {
    const wrapper = mount(CitationTooltip, {
      props: {
        source: '我的资料库 · docx',
        title: '春旧教案',
        knowledgeType: 'personal_asset',
        snippet: '朗读课文，圈画关键词。',
      },
    });

    expect(wrapper.text()).toContain('我的资料');
    await wrapper.trigger('mouseenter');
    expect(wrapper.text()).toContain('我的资料库 · docx');
  });
});
