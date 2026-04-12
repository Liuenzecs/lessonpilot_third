import { defineStore } from 'pinia';

export interface BillingDialogState {
  open: boolean;
  reason: 'quota_exceeded' | 'plan_required' | 'upgrade';
  title: string;
  description: string;
  initialCycle: 'monthly' | 'yearly';
}

export const useBillingDialogStore = defineStore('billing-dialog', {
  state: (): BillingDialogState => ({
    open: false,
    reason: 'upgrade',
    title: '升级到专业版',
    description: '解锁局部 AI、PDF 导出、版本历史和不限量备课。',
    initialCycle: 'yearly',
  }),
  actions: {
    openDialog(payload?: Partial<Omit<BillingDialogState, 'open'>>) {
      this.open = true;
      this.reason = payload?.reason ?? 'upgrade';
      this.title = payload?.title ?? '升级到专业版';
      this.description = payload?.description ?? '解锁局部 AI、PDF 导出、版本历史和不限量备课。';
      this.initialCycle = payload?.initialCycle ?? 'yearly';
    },
    closeDialog() {
      this.open = false;
    },
  },
});
