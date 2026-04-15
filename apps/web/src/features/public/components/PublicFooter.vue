<script setup lang="ts">
import { RouterLink } from 'vue-router';
</script>

<template>
  <footer class="public-footer">
    <div class="public-footer-grid">
      <div>
        <div class="public-footer-brand">LessonPilot</div>
        <p class="public-footer-copy">备课助手，让备课不再是负担。</p>
      </div>

      <div>
        <div class="public-footer-title">产品</div>
        <RouterLink :to="{ name: 'landing', hash: '#features' }">功能介绍</RouterLink>
        <RouterLink :to="{ name: 'pricing' }">定价</RouterLink>
        <RouterLink :to="{ name: 'changelog' }">更新日志</RouterLink>
      </div>

      <div>
        <div class="public-footer-title">支持</div>
        <RouterLink :to="{ name: 'help' }">帮助中心</RouterLink>
        <RouterLink :to="{ name: 'about' }">联系我们</RouterLink>
        <a href="mailto:hello@lessonpilot.com">反馈建议</a>
      </div>

      <div>
        <div class="public-footer-title">法律</div>
        <RouterLink :to="{ name: 'privacy' }">隐私政策</RouterLink>
        <RouterLink :to="{ name: 'terms' }">服务条款</RouterLink>
      </div>
    </div>

    <div class="public-footer-bottom">
      <span>© 2026 LessonPilot. All rights reserved.</span>
      <span>备案号：沪ICP备2026000001号</span>
      <span>公安备案：沪公网安备2026000001号</span>
    </div>
  </footer>
</template>
