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

export interface AccountDeletePayload {
  confirm_text: string;
}

export interface TeacherStyleProfile {
  id: string | null;
  enabled: boolean;
  objective_style: string;
  process_style: string;
  school_wording: string;
  activity_preferences: string;
  avoid_phrases: string;
  sample_count: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface TeacherStyleProfileUpdatePayload {
  enabled: boolean;
  objective_style: string;
  process_style: string;
  school_wording: string;
  activity_preferences: string;
  avoid_phrases: string;
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
