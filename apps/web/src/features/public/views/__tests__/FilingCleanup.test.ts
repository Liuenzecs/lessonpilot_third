import { mount, RouterLinkStub } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { createMemoryHistory } from 'vue-router';
import { describe, expect, it } from 'vitest';

import { createAppRouter } from '@/app/router';
import PublicFooter from '@/features/public/components/PublicFooter.vue';
import PublicNav from '@/features/public/components/PublicNav.vue';
import { helpGroups, termsSections } from '@/features/public/content';

const commercialTerms = ['定价', '付费', '会员', '套餐', '订阅', '支付', '退款', '升级到专业版', '专业版', '免费版'];

function expectNoCommercialCopy(text: string) {
  for (const term of commercialTerms) {
    expect(text).not.toContain(term);
  }
}

describe('filing commercial cleanup', () => {
  it('hides commercial links from public navigation and footer', async () => {
    const pinia = createPinia();
    const router = createAppRouter(pinia, createMemoryHistory());
    await router.push('/');
    await router.isReady();

    const nav = mount(PublicNav, {
      global: {
        plugins: [pinia, router],
      },
    });
    const footer = mount(PublicFooter, {
      global: {
        stubs: {
          RouterLink: RouterLinkStub,
        },
      },
    });

    expectNoCommercialCopy(nav.text());
    expectNoCommercialCopy(footer.text());
  });

  it('redirects /pricing to the landing page', async () => {
    const router = createAppRouter(createPinia(), createMemoryHistory());
    await router.push('/pricing');
    await router.isReady();

    expect(router.currentRoute.value.name).toBe('landing');
    expect(router.currentRoute.value.path).toBe('/');
  });

  it('removes commercial wording from help and terms content', () => {
    const helpText = JSON.stringify(helpGroups);
    const termsText = JSON.stringify(termsSections);

    expectNoCommercialCopy(helpText);
    expectNoCommercialCopy(termsText);
  });
});
