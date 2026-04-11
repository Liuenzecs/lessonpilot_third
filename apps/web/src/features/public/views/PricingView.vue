<script setup lang="ts">
import { computed, ref } from 'vue';
import { RouterLink } from 'vue-router';

import FaqAccordion from '@/features/public/components/FaqAccordion.vue';
import { pricingFaqs } from '@/features/public/content';

const billingCycle = ref<'monthly' | 'yearly'>('yearly');

const pricingCards = computed(() => [
  {
    title: '免费版',
    price: '¥0',
    secondary: '',
    badge: '',
    disabled: false,
    cta: '免费开始',
    to: { name: 'register' },
    features: ['每月 5 份教案参考额度', '基础编辑', 'Word 导出'],
  },
  {
    title: '专业版',
    price: billingCycle.value === 'monthly' ? '¥29/月' : '¥19/月',
    secondary: billingCycle.value === 'monthly' ? '按月支付' : '年付均价，省 20%',
    badge: '推荐',
    disabled: false,
    cta: '开始免费试用',
    to: { name: 'register' },
    features: ['无限生成', '局部 AI 重写', 'Word + PDF 导出', '版本历史', '所有学科模板'],
  },
  {
    title: '团队版',
    price: billingCycle.value === 'monthly' ? '¥99/月' : '¥69/月',
    secondary: '即将推出',
    badge: '',
    disabled: true,
    cta: '联系我们',
    to: { name: 'about' },
    features: ['专业版全部能力', '5 个成员', '共享资产库', '优先客服'],
  },
]);
</script>

<template>
  <div class="pricing-page">
    <section class="pricing-hero section-card">
      <p class="page-eyebrow">定价页</p>
      <h1 class="page-title">选择适合你的方案</h1>
      <p class="subtitle">所有方案都包含核心备课能力，先用起来，再决定是否升级。</p>

      <div class="pricing-toggle">
        <button :class="{ active: billingCycle === 'monthly' }" type="button" @click="billingCycle = 'monthly'">
          月付
        </button>
        <button :class="{ active: billingCycle === 'yearly' }" type="button" @click="billingCycle = 'yearly'">
          年付（省 20%）
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

        <RouterLink class="button" :class="card.title === '专业版' ? 'primary' : 'ghost'" :to="card.to">
          {{ card.cta }}
        </RouterLink>
      </article>
    </section>

    <section class="section-card">
      <div class="landing-section-head">
        <p class="page-eyebrow">常见定价问题</p>
        <h2>先把最关心的问题说清楚</h2>
      </div>
      <FaqAccordion :items="pricingFaqs" />
    </section>
  </div>
</template>
