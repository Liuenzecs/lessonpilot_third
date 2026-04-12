import type { AuthUser } from '@/features/auth/types';

export type AccountRead = AuthUser;

export interface AccountUpdatePayload {
  name?: string;
  email?: string;
}

export interface AccountChangePasswordPayload {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface AccountSubscriptionRead {
  plan: 'free' | 'professional';
  plan_label: string;
  status: 'free' | 'trialing' | 'active' | 'expired';
  is_paid: boolean;
  billing_cycle: 'monthly' | 'yearly' | null;
  trial_started_at: string | null;
  trial_ends_at: string | null;
  current_period_start: string | null;
  current_period_end: string | null;
  tasks_used_this_month: number;
  next_renewal_at: string | null;
  monthly_task_limit: number | null;
  quota_remaining: number | null;
  trial_used: boolean;
  entitlements: SubscriptionEntitlementsRead;
}

export interface SubscriptionEntitlementsRead {
  monthly_task_limit: number | null;
  word_export: boolean;
  pdf_export: boolean;
  ai_rewrite: boolean;
  ai_append: boolean;
  section_regenerate: boolean;
  version_history: boolean;
  all_subject_presets: boolean;
}

export interface SubscriptionCheckoutPayload {
  plan: 'professional';
  billing_cycle: 'monthly' | 'yearly';
  channel: 'wechat' | 'alipay';
}

export interface BillingOrderRecord {
  id: string;
  plan: 'professional';
  billing_cycle: 'monthly' | 'yearly';
  channel: 'wechat' | 'alipay';
  amount_cents: number;
  status: 'pending' | 'paid' | 'failed' | 'expired';
  checkout_url: string | null;
  external_order_id: string | null;
  paid_at: string | null;
  effective_at: string | null;
  created_at: string;
}

export interface BillingOrderListResponse {
  items: BillingOrderRecord[];
}

export interface SubscriptionActionResponse {
  subscription: AccountSubscriptionRead;
  order: BillingOrderRecord | null;
  message: string;
}

export interface InvoiceRequestCreatePayload {
  order_id: string;
  title: string;
  tax_number: string;
  email: string;
  remark?: string | null;
}

export interface InvoiceRequestRecord {
  id: string;
  order_id: string;
  title: string;
  tax_number: string;
  email: string;
  remark: string | null;
  status: 'submitted';
  created_at: string;
}

export interface InvoiceRequestListResponse {
  items: InvoiceRequestRecord[];
}

export interface AccountDeletePayload {
  confirm_text: string;
}

export interface FeedbackCreatePayload {
  mood: 'happy' | 'neutral' | 'sad';
  message: string;
  page_path?: string;
}

export interface FeedbackRead {
  id: string;
  user_id: string;
  mood: 'happy' | 'neutral' | 'sad';
  message: string;
  page_path: string | null;
  created_at: string;
}
