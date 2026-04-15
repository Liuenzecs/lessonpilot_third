<script setup lang="ts">
import { BookOpenText, FileDown, WandSparkles } from 'lucide-vue-next';
import { RouterView } from 'vue-router';

import PublicFooter from '@/features/public/components/PublicFooter.vue';
import PublicNav from '@/features/public/components/PublicNav.vue';

import '@/features/public/styles/public.css';
</script>

<template>
  <div class="auth-shell">
    <PublicNav />

    <main class="auth-shell-main">
      <section class="auth-brand-panel section-card">
        <p class="page-eyebrow">LessonPilot</p>
        <h1>今晚的课，今晚就能备好</h1>
        <p class="auth-brand-text">
          结构可见，操作极简。老师不需要先学一套复杂工具，打开就能开始备课。
        </p>
        <div class="auth-brand-points">
          <article class="auth-brand-point app-card">
            <WandSparkles :size="20" />
            <div>
              <strong>3 步完成创建</strong>
              <p>选学科、选年级、填主题，直接进入编辑器。</p>
            </div>
          </article>
          <article class="auth-brand-point app-card">
            <BookOpenText :size="20" />
            <div>
              <strong>自动生成骨架</strong>
              <p>结构化教案自动生成，老师只需要编辑和把关。</p>
            </div>
          </article>
          <article class="auth-brand-point app-card">
            <FileDown :size="20" />
            <div>
              <strong>导出即可使用</strong>
              <p>确认过的内容能直接导出成 Word 或 PDF。</p>
            </div>
          </article>
        </div>
      </section>

      <div class="auth-form-panel">
        <RouterView />
      </div>
    </main>

    <PublicFooter />
  </div>
</template>
