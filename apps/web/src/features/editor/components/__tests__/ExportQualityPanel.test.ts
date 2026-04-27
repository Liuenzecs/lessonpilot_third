import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import ExportQualityPanel from '../ExportQualityPanel.vue';

describe('ExportQualityPanel', () => {
  it('renders needs-fixes issues and allows export', async () => {
    const wrapper = mount(ExportQualityPanel, {
      props: {
        open: true,
        loading: false,
        fixing: false,
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
          alignment_map: [],
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
        fixing: false,
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
          alignment_map: [],
        },
      },
    });

    expect(wrapper.text()).toContain('暂不建议导出');
    expect(wrapper.find('.button.primary').attributes('disabled')).toBeDefined();
  });

  it('renders alignment map when quality v2 returns it', () => {
    const wrapper = mount(ExportQualityPanel, {
      props: {
        open: true,
        loading: false,
        fixing: false,
        result: {
          readiness: 'needs_fixes',
          summary: '目标过程评价需要再对齐。',
          issues: [],
          warnings: [],
          suggestions: [],
          alignment_map: [
            {
              objective: '品味比喻拟人句的表达效果',
              process_matches: ['品味语言'],
              assessment_matches: [],
              status: 'partial',
            },
          ],
        },
      },
    });

    expect(wrapper.text()).toContain('目标-过程-评价');
    expect(wrapper.text()).toContain('品味比喻拟人句');
  });

  it('emits fix for supported quality issues', async () => {
    const wrapper = mount(ExportQualityPanel, {
      props: {
        open: true,
        loading: false,
        fixing: false,
        result: {
          readiness: 'needs_fixes',
          summary: '建议处理。',
          issues: [
            {
              severity: 'warning',
              section: 'objectives',
              message: '教学目标第 1 条表述偏空泛。',
              suggestion: '改成可观察目标。',
            },
          ],
          warnings: [],
          suggestions: [],
          alignment_map: [],
        },
      },
    });

    await wrapper.find('.quality-fix-btn').trigger('click');
    expect(wrapper.emitted('fix')).toHaveLength(1);
  });
});
