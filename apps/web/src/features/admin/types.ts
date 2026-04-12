import type { AccountSubscriptionRead, BillingOrderRecord, FeedbackRead } from '@/features/settings/types';
import type { AuthUser } from '@/features/auth/types';
import type { TaskRecord } from '@/features/task/types';

export interface AdminOverviewMetric {
  key: string;
  label: string;
  value: number;
}

export interface AdminOverviewRead {
  last_7_days: AdminOverviewMetric[];
  last_30_days: AdminOverviewMetric[];
}

export interface AdminUserListItemRead {
  user: AuthUser;
  subscription: AccountSubscriptionRead;
}

export interface AdminUserListResponse {
  items: AdminUserListItemRead[];
  total: number;
}

export interface QuotaAdjustmentRecord {
  id: string;
  user_id: string;
  applied_by_user_id: string;
  month_key: string;
  delta: number;
  reason: string | null;
  created_at: string;
}

export interface QuotaAdjustmentListResponse {
  items: QuotaAdjustmentRecord[];
}

export interface QuotaAdjustmentCreatePayload {
  delta: number;
  reason?: string | null;
  month_key?: string | null;
}

export interface AdminUserDetailRead {
  user: AuthUser;
  subscription: AccountSubscriptionRead;
  latest_paid_order: BillingOrderRecord | null;
  recent_tasks: TaskRecord[];
  recent_feedback: FeedbackRead[];
  quota_adjustments: QuotaAdjustmentRecord[];
}
