<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import FaqAccordion from '@/features/public/components/FaqAccordion.vue';
import { pricingFaqs } from '@/features/public/content';

const router = useRouter();
const authStore = useAuthStore();
const billingCycle = ref<'monthly' | 'yearly'>('yearly');

const pricingCards = computed(() => [
  {
    title: '免费版',
    price: '¥0',
    secondary: '适合先体验产品主链路',
    badge: '',
    disabled: false,
    cta: authStore.isAuthenticated ? '进入备课台' : '免费开始',
    action: () => router.push(authStore.isAuthenticated ? { name: 'tasks' } : { name: 'register' }),
    features: ['每月 5 份教案额度', '基础编辑', 'Word 导出'],
  },
  {
    title: '专业版',
    price: billingCycle.value === 'monthly' ? '¥29/月' : '¥228/年',
    secondary: billingCycle.value === 'monthly' ? '手动续费，不自动扣费' : '折合 ¥19/月，手动续费',
    badge: '推荐',
    disabled: false,
    cta: '开始试用或支付',
    action: () => {
      if (authStore.isAuthenticated) {
        void router.push({ name: 'settings' });
        return;
      }
      void router.push({ name: 'register' });
    },
    features: ['不限量教案生成', '局部 AI 重写与补充', 'Word + PDF 导出', '版本历史', '官方预设全覆盖'],
  },
  {
    title: '团队版',
    price: '即将推出',
    secondary: '暂不开放真实购买',
    badge: '',
    disabled: true,
    cta: '敬请期待',
    action: () => undefined,
    features: ['专业版全部能力', '多人协作与共享资产', '专属支持'],
  },
]);
</script>

<template>
  <div class="pricing-page">
    <section class="pricing-hero section-card">
      <p class="page-eyebrow">定价页</p>
      <h1 class="page-title">选择适合你的方案</h1>
      <p class="subtitle">免费版先上手，专业版通过试用或手动续费完成升级，不做自动代扣。</p>

      <div class="pricing-toggle">
        <button :class="{ active: billingCycle === 'monthly' }" type="button" @click="billingCycle = 'monthly'">
          月付
        </button>
        <button :class="{ active: billingCycle === 'yearly' }" type="button" @click="billingCycle = 'yearly'">
          年付（更划算）
        </button>
      </div>
    </section>

    <section class="pricing-grid">
      <article
        v-for="card in pricingCards"
        :key="card.title"
        class="pricing-card app-card"
        :class="{ featured: card.title === '专业版', disabled: card.disabled }"
      >
        <div class="pricing-card-head">
          <div>
            <p class="pricing-plan">{{ card.title }}</p>
            <h2>{{ card.price }}</h2>
            <p class="subtitle">{{ card.secondary }}</p>
          </div>
          <span v-if="card.badge" class="pricing-badge">{{ card.badge }}</span>
        </div>

        <ul class="pricing-feature-list">
          <li v-for="feature in card.features" :key="feature">✓ {{ feature }}</li>
        </ul>

        <button
          class="button"
          :class="card.title === '专业版' ? 'primary' : 'ghost'"
          type="button"
          :disabled="card.disabled"
          @click="card.action()"
        >
          {{ card.cta }}
        </button>
      </article>
    </section>

    <section class="section-card">
      <div class="landing-section-head">
        <p class="page-eyebrow">常见定价问题</p>
        <h2>把最关心的付费细节说清楚</h2>
      </div>
      <FaqAccordion :items="pricingFaqs" />
    </section>
  </div>
</template>
