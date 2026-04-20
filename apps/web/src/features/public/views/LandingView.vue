<script setup lang="ts">
import { BookOpenText, Clock3, Files, FolderOpen, GraduationCap, House } from 'lucide-vue-next';

import { RouterLink } from 'vue-router';


import HeroProductPreview from '@/features/public/components/HeroProductPreview.vue';
import { landingFeatures, landingPainPoints, landingPersonas } from '@/features/public/content';


const landingIcons = {
  book: BookOpenText,
  clock: Clock3,
  files: Files,
  folder: FolderOpen,
  graduate: GraduationCap,
  home: House,
} as const;

function resolveLandingIcon(icon: string) {
  return landingIcons[icon as keyof typeof landingIcons] ?? BookOpenText;
}
</script>

<template>
  <div class="landing-page">
    <section class="landing-hero">
      <div class="landing-hero-copy">
        <p class="page-eyebrow">结构可见，操作极简</p>
        <h1>10 分钟，搞定一份好教案</h1>
        <p class="landing-hero-text">
          输入课题，先整理出完整初稿，你来调整和把关。选学科、定主题，LessonPilot 会把骨架和主要内容先铺开。
        </p>
        <div class="button-row landing-hero-actions">
          <RouterLink class="button primary" :to="{ name: 'register' }" @click="(() => {})">
            免费开始备课
          </RouterLink>
          <RouterLink class="landing-link" :to="{ name: 'login' }" @click="(() => {})">
            已有账号？登录 →
          </RouterLink>
        </div>
      </div>

      <HeroProductPreview />
    </section>

    <section class="landing-section section-card alt-bg">
      <div class="landing-section-head">
        <p class="page-eyebrow">痛点共鸣</p>
        <h2>备课，不该这么累</h2>
      </div>
      <div class="landing-pain-grid">
        <article v-for="item in landingPainPoints" :key="item.title" class="landing-pain-card">
          <div class="landing-card-icon" aria-hidden="true">
            <component :is="resolveLandingIcon(item.icon)" :size="26" />
          </div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </article>
      </div>
    </section>

    <section id="features" class="landing-section">
      <div class="landing-section-head">
        <p class="page-eyebrow">核心功能</p>
        <h2>老师打开就知道下一步该点哪里</h2>
      </div>

      <div
        v-for="(feature, index) in landingFeatures"
        :key="feature.id"
        class="feature-row"
        :class="{ reverse: index % 2 === 1 }"
      >
        <div class="feature-preview">
          <div class="feature-preview-top">
            <span class="feature-index">{{ feature.index }}</span>
            <span class="feature-preview-badge">真实产品流程</span>
          </div>
          <div class="feature-preview-stack">
            <div class="feature-preview-panel strong">{{ feature.title }}</div>
            <div class="feature-preview-panel">{{ feature.bullets[0] }}</div>
            <div class="feature-preview-panel muted">{{ feature.bullets[1] }}</div>
          </div>
        </div>

        <div class="feature-copy">
          <div class="feature-index big">{{ feature.index }}</div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
          <ul class="feature-bullets">
            <li v-for="bullet in feature.bullets" :key="bullet">{{ bullet }}</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="landing-section section-card alt-bg">
      <div class="landing-section-head">
        <p class="page-eyebrow">使用场景</p>
        <h2>谁在用 LessonPilot？</h2>
      </div>
      <div class="persona-grid">
        <article v-for="persona in landingPersonas" :key="persona.title" class="persona-card">
          <div class="landing-card-icon" aria-hidden="true">
            <component :is="resolveLandingIcon(persona.icon)" :size="26" />
          </div>
          <h3>{{ persona.title }}</h3>
          <p>{{ persona.problem }}</p>
          <p class="persona-value">{{ persona.value }}</p>
        </article>
      </div>
    </section>

    <section class="landing-cta">
      <p class="page-eyebrow">立即开始</p>
      <h2>今晚的课，现在就能备好</h2>
      <RouterLink
        class="button primary landing-cta-button"
        :to="{ name: 'register' }"
        @click="(() => {})"
      >
        免费开始备课
      </RouterLink>
      <p class="subtitle">无需信用卡 · 免费额度足够先把流程跑通</p>
    </section>
  </div>
</template>
