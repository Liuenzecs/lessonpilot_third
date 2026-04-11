<script setup lang="ts">
import LegalDocumentPage from '@/features/public/components/LegalDocumentPage.vue';
import { privacySections } from '@/features/public/content';
</script>

<template>
  <LegalDocumentPage title="隐私政策" updated-at="2026-04-11" :sections="privacySections" />
</template>
