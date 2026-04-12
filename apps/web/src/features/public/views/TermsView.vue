<script setup lang="ts">
import LegalDocumentPage from '@/features/public/components/LegalDocumentPage.vue';
import { termsSections } from '@/features/public/content';
</script>

<template>
  <LegalDocumentPage title="服务条款" updated-at="2026-04-12" :sections="termsSections" />
</template>
