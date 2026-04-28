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
        <p class="page-eyebrow">教师文档桌</p>
        <h1><span>教案能交，</span><span>也能上课</span></h1>
        <p class="landing-hero-text">
          输入课题或导入旧 Word，LessonPilot 会先整理出完整初稿，再把知识引用、质量体检和学校格式导出放在同一张备课桌上。
        </p>
        <div class="button-row landing-hero-actions">
          <RouterLink class="button primary" :to="{ name: 'register' }" @click="(() => {})">
            试做一份教案
          </RouterLink>
          <RouterLink class="landing-link" :to="{ name: 'login' }" @click="(() => {})">
            导入旧教案看看 →
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
        <p class="page-eyebrow">核心工作流</p>
        <h2>从旧资料到学校 Word，路径短一点</h2>
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
      <h2>今晚要交的教案，先放到文档桌上</h2>
      <RouterLink
        class="button primary landing-cta-button"
        :to="{ name: 'register' }"
        @click="(() => {})"
      >
        试做一份教案
      </RouterLink>
      <p class="subtitle">无需信用卡 · 免费额度足够先把流程跑通</p>
    </section>
  </div>
</template>
