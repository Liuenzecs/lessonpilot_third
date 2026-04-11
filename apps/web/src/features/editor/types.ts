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

export interface DocumentRewritePayload {
  document_version: number;
  mode: 'block' | 'selection';
  target_block_id: string;
  action: 'rewrite' | 'polish' | 'expand';
  selection_text?: string | null;
}

export interface DocumentRewriteStartResponse {
  stream_url: string;
}

export interface DocumentAppendPayload {
  document_version: number;
  section_id: string;
  instruction: string;
}

export interface DocumentAppendStartResponse {
  stream_url: string;
}

export interface DocumentSnapshotRecord {
  id: string;
  document_id: string;
  version: number;
  content: ContentDocument;
  source: string;
  created_at: string;
}

export interface DocumentHistoryResponse {
  items: DocumentSnapshotRecord[];
}
