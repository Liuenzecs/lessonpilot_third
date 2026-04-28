import type { LessonCategory, LessonPlanContent, LessonType, Scene } from '@lessonpilot/shared-types';
import type { LessonDocument } from '@/features/editor/types';

export interface TemplateRecord {
  id: string;
  user_id?: string | null;
  name: string;
  subject: string;
  grade: string;
  description: string | null;
  template_type: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface TemplateFieldMapping {
  template_label: string;
  content_field: string;
  confidence: number;
  location: string;
}

export interface TemplateTableLayout {
  name: string;
  columns: string[];
  field_mappings: TemplateFieldMapping[];
}

export interface SchoolTemplatePreview {
  source_filename: string;
  name: string;
  subject: string;
  grade: string;
  template_type: string;
  field_mappings: TemplateFieldMapping[];
  section_order: string[];
  table_layouts: TemplateTableLayout[];
  blank_areas: string[];
  unsupported_items: string[];
  warnings: string[];
}

export interface SchoolTemplateConfirmPayload {
  preview: SchoolTemplatePreview;
  name?: string | null;
  subject?: string | null;
  grade?: string | null;
}

export interface ExtractedAssetSection {
  title: string;
  content: string;
  section_type: string;
}

export interface ReuseSuggestion {
  target: string;
  label: string;
  reason: string;
}

export interface PersonalAssetPreview {
  source_filename: string;
  file_type: 'docx' | 'pptx';
  title: string;
  subject: string;
  grade: string;
  topic: string;
  asset_type: 'lesson_plan' | 'study_guide' | 'ppt_outline' | 'teaching_note' | 'reference_material';
  extracted_sections: ExtractedAssetSection[];
  unmapped_sections: ExtractedAssetSection[];
  reuse_suggestions: ReuseSuggestion[];
  warnings: string[];
}

export interface PersonalAssetRecord {
  id: string;
  title: string;
  asset_type: string;
  source_filename: string;
  file_type: string;
  subject: string;
  grade: string;
  topic: string;
  extracted_content: Record<string, unknown>;
  reuse_suggestions: ReuseSuggestion[];
  created_at: string;
  updated_at: string;
}

export interface PersonalAssetRecommendation {
  asset_id: string;
  title: string;
  asset_type: string;
  file_type: string;
  source_filename: string;
  subject: string;
  grade: string;
  topic: string;
  section_title: string;
  section_type: string;
  content_snippet: string;
  score: number;
  matched_terms: string[];
}

export interface PersonalAssetConfirmPayload {
  preview: PersonalAssetPreview;
  title?: string | null;
  subject?: string | null;
  grade?: string | null;
  topic?: string | null;
  asset_type?: PersonalAssetPreview['asset_type'] | null;
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

export interface GenerationStartPayload {
  section_id?: string | null;
  use_personal_assets?: boolean;
  personal_asset_ids?: string[];
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

// ---------------------------------------------------------------------------
// Batch import types
// ---------------------------------------------------------------------------

export interface BatchImportPreview {
  items: LessonPlanImportPreview[];
}

export interface BatchImportConfirmPayload {
  items: LessonPlanImportConfirmPayload[];
}

export interface BatchImportFailure {
  source_filename: string;
  error: string;
}

export interface BatchImportConfirmResponse {
  items: LessonPlanImportConfirmResponse[];
  total: number;
  succeeded: number;
  failed: number;
  failures: BatchImportFailure[];
}
