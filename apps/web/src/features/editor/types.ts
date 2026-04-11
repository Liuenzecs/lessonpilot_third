import type { ContentDocument } from '@lessonpilot/shared-types';

export interface LessonDocument {
  id: string;
  task_id: string;
  user_id: string;
  doc_type: string;
  title: string;
  content: ContentDocument;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  items: LessonDocument[];
}

export interface DocumentUpdatePayload {
  version: number;
  content: ContentDocument;
}

