import type { LessonCategory, LessonType, Scene } from '@lessonpilot/shared-types';

export interface TaskRecord {
  id: string;
  title: string;
  subject: string;
  grade: string;
  topic: string;
  requirements: string | null;
  status: string;
  scene: Scene;
  lesson_type: LessonType;
  class_hour: number;
  lesson_category: LessonCategory;
  created_at: string;
  updated_at: string;
}

export interface PaginatedTasks {
  items: TaskRecord[];
  page: number;
  page_size: number;
  total: number;
}

export interface TaskCreatePayload {
  subject: string;
  grade: string;
  topic: string;
  requirements?: string | null;
  title?: string | null;
  scene?: Scene;
  lesson_type?: LessonType;
  class_hour?: number;
  lesson_category?: LessonCategory;
}

export interface TaskUpdatePayload {
  title?: string | null;
  requirements?: string | null;
  status?: string | null;
}

export interface GenerationStartResponse {
  stream_url: string;
}
