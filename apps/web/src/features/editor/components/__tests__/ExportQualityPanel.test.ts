import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import ExportQualityPanel from '../ExportQualityPanel.vue';

describe('ExportQualityPanel', () => {
  it('renders needs-fixes issues and allows export', async () => {
    const wrapper = mount(ExportQualityPanel, {
      props: {
        open: true,
        loading: false,
        result: {
          readiness: 'needs_fixes',
          summary: '有 1 个提交前建议处理的问题。',
          issues: [
            {
              severity: 'warning',
              section: 'objectives',
              message: '教学目标仍处于待确认。',
              suggestion: '确认教学目标后再导出。',
            },
          ],
          warnings: [],
          suggestions: [],
        },
      },
    });

    expect(wrapper.text()).toContain('建议先处理');
    expect(wrapper.text()).toContain('教学目标仍处于待确认');
    await wrapper.find('.button.primary').trigger('click');
    expect(wrapper.emitted('export')).toHaveLength(1);
  });

  it('disables export for blocked documents', () => {
    const wrapper = mount(ExportQualityPanel, {
      props: {
        open: true,
        loading: false,
        result: {
          readiness: 'blocked',
          summary: '有 1 个阻断问题，暂不建议直接导出。',
          issues: [
            {
              severity: 'blocker',
              section: null,
              message: '当前文档几乎没有可导出的教案内容。',
              suggestion: '先生成、导入或补写正文内容。',
            },
          ],
          warnings: [],
          suggestions: [],
        },
      },
    });

    expect(wrapper.text()).toContain('暂不建议导出');
    expect(wrapper.find('.button.primary').attributes('disabled')).toBeDefined();
  });
});
