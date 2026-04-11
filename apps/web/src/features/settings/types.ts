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
  is_paid: boolean;
  monthly_task_limit: number;
  tasks_used_this_month: number;
  next_renewal_at: string | null;
}

export interface AccountDeletePayload {
  confirm_text?: string;
  password?: string;
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
