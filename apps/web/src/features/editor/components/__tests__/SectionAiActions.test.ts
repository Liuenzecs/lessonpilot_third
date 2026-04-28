import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import SectionAiActions from '../SectionAiActions.vue';

describe('SectionAiActions', () => {
  it('renders the relabeled helper actions', async () => {
    const wrapper = mount(SectionAiActions);

    expect(wrapper.get('.ai-trigger-btn').text()).toBe('调整');

    await wrapper.get('.ai-trigger-btn').trigger('click');

    const items = wrapper.findAll('.ai-menu-item').map((item) => item.text());
    expect(items).toContain('改写');
    expect(items).toContain('补充展开');
    expect(items).toContain('压缩表达');
    expect(items).toContain('自定义指令...');
  });

  it('keeps the existing action payload contract', async () => {
    const wrapper = mount(SectionAiActions);

    await wrapper.get('.ai-trigger-btn').trigger('click');
    await wrapper.findAll('.ai-menu-item')[0].trigger('click');

    expect(wrapper.emitted('action')).toEqual([
      [{ action: 'rewrite', instruction: '' }],
    ]);
  });
});
