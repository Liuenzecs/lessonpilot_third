<template>
  <section class="section-card" style="text-align:center; padding: 64px 24px;">
    <p class="page-eyebrow">定价方案</p>
    <h1 class="page-title">定价页面建设中</h1>
    <p class="subtitle" style="margin-bottom:28px;">LessonPilot 当前免费使用，未来上线更多增值方案后会在这里公布。</p>
    <RouterLink class="button primary" :to="{ name: 'landing' }">返回首页</RouterLink>
  </section>
</template>

<script lang="ts">
import { RouterLink } from 'vue-router';
export default { components: { RouterLink } };
</script>
