import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import EditorStatusBanner from '../EditorStatusBanner.vue';

function mountBanner(overrides: Record<string, unknown> = {}) {
  return mount(EditorStatusBanner, {
    props: {
      isGenerating: false,
      completed: 0,
      total: 0,
      currentSection: '',
      ragStatus: null,
      assetStatus: null,
      isRewriting: false,
      rewriteAction: 'rewrite',
      isAppending: false,
      appendSectionTitle: '',
      streamError: '',
      noticeText: '',
      noticeTone: 'success',
      ...overrides,
    },
  });
}

describe('EditorStatusBanner', () => {
  it('renders ready rag status with domain and count', () => {
    const wrapper = mountBanner({
      ragStatus: {
        status: 'ready',
        domain: '春',
        matched_keywords: ['春朱自清'],
        chunk_count: 3,
        retrieved_count: 2,
        message: '已命中“春”知识包，本次会参考相关资料生成。',
      },
    });

    expect(wrapper.text()).toContain('已命中“春”知识包');
    expect(wrapper.text()).toContain('春 · 2/3 条');
  });

  it('renders degraded rag status without exposing internals', () => {
    const wrapper = mountBanner({
      ragStatus: {
        status: 'degraded',
        domain: '红楼梦',
        matched_keywords: ['红楼梦'],
        chunk_count: 5,
        retrieved_count: 0,
        message: '知识增强检索暂时不可用，本次已自动降级为普通生成。',
      },
    });

    expect(wrapper.text()).toContain('自动降级为普通生成');
    expect(wrapper.text()).not.toContain('Traceback');
  });

  it('renders personal asset status with source counts', () => {
    const wrapper = mountBanner({
      assetStatus: {
        status: 'ready',
        matched_assets: [{ asset_id: 'asset-1', title: '春旧教案', file_type: 'docx' }],
        snippet_count: 2,
        message: '已命中 1 份我的资料，本次会参考相关片段生成。',
      },
    });

    expect(wrapper.text()).toContain('我的资料');
    expect(wrapper.text()).toContain('1 份');
    expect(wrapper.text()).toContain('2 段');
  });
});
