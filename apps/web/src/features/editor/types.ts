import type { DocumentContent } from '@lessonpilot/shared-types';

export interface LessonDocument {
  id: string;
  task_id: string;
  user_id: string;
  doc_type: 'lesson_plan' | 'study_guide';
  title: string;
  content: DocumentContent;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  items: LessonDocument[];
}

export interface DocumentUpdatePayload {
  version: number;
  content: DocumentContent;
}

export interface DocumentRewritePayload {
  document_version: number;
  section_name: string;
  action: 'rewrite' | 'expand' | 'simplify';
  instruction?: string | null;
}

export interface DocumentRewriteStartResponse {
  stream_url: string;
}

export interface DocumentSnapshotRecord {
  id: string;
  document_id: string;
  version: number;
  content: DocumentContent;
  source: string;
  created_at: string;
}

export interface DocumentHistoryResponse {
  items: DocumentSnapshotRecord[];
}

export type QualityReadiness = 'ready' | 'needs_fixes' | 'blocked';

export interface QualityIssue {
  severity: 'blocker' | 'warning' | 'suggestion';
  section: string | null;
  message: string;
  suggestion: string;
}

export interface QualityFixPayload {
  section: string | null;
  message: string;
  suggestion: string;
}

export interface QualityCheckResponse {
  readiness: QualityReadiness;
  summary: string;
  issues: QualityIssue[];
  warnings: QualityIssue[];
  suggestions: QualityIssue[];
  alignment_map: Array<{
    objective: string;
    process_matches: string[];
    assessment_matches: string[];
    status: 'covered' | 'partial' | 'missing';
  }>;
}

export interface PptSlideDraft {
  title: string;
  bullets: string[];
  activity: string;
  speaker_note: string;
  status: string;
}

export interface TalkScriptDraft {
  opening: string;
  questions: string[];
  transitions: string[];
  closing: string;
  status: string;
}

export interface TeachingPackageRecord {
  id: string;
  task_id: string;
  document_id: string;
  title: string;
  status: string;
  content: {
    study_guide: Extract<DocumentContent, { doc_type: 'study_guide' }>;
    ppt_outline: PptSlideDraft[];
    talk_script: TalkScriptDraft;
  };
  created_at: string;
  updated_at: string;
}
