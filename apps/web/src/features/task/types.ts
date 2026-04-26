import type { LessonCategory, LessonPlanContent, LessonType, Scene } from '@lessonpilot/shared-types';
import type { LessonDocument } from '@/features/editor/types';

export interface TemplateRecord {
  id: string;
  name: string;
  subject: string;
  grade: string;
  description: string | null;
  template_type: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

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
  template_id: string | null;
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
  template_id?: string | null;
}

export interface TaskUpdatePayload {
  title?: string | null;
  requirements?: string | null;
  status?: string | null;
}

export interface GenerationStartResponse {
  stream_url: string;
}

export interface ImportWarning {
  severity: 'info' | 'warning';
  section: string | null;
  message: string;
}

export interface UnmappedSection {
  title: string | null;
  content: string;
}

export interface LessonPlanImportMetadata {
  title: string;
  subject: string;
  grade: string;
  topic: string;
  class_hour: number;
  lesson_category: LessonCategory;
  scene: Scene;
}

export interface LessonPlanImportPreview {
  source_filename: string;
  metadata: LessonPlanImportMetadata;
  content: LessonPlanContent;
  mapped_sections: string[];
  unmapped_sections: UnmappedSection[];
  warnings: ImportWarning[];
}

export interface LessonPlanImportConfirmPayload {
  metadata: LessonPlanImportMetadata;
  content: LessonPlanContent;
}

export interface LessonPlanImportConfirmResponse {
  task: TaskRecord;
  document: LessonDocument;
}
