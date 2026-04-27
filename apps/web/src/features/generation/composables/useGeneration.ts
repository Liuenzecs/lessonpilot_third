import { buildApiUrl } from '@/shared/api/client';
import type { LessonDocument } from '@/features/editor/types';

export interface CitationInfo {
  chunk_id: string;
  source: string;
  title: string;
  knowledge_type: string;
  chapter?: string;
  content_snippet: string;
}

export interface RagStatusInfo {
  status: 'disabled' | 'unmatched' | 'matched_empty' | 'ready' | 'degraded';
  domain?: string | null;
  matched_keywords: string[];
  chunk_count: number;
  retrieved_count: number;
  message: string;
}

export interface AssetStatusInfo {
  status: 'disabled' | 'unmatched' | 'ready' | 'degraded';
  matched_assets: Array<{
    asset_id: string;
    title: string;
    file_type: string;
  }>;
  snippet_count: number;
  message: string;
}

export interface SectionDocumentPayload extends LessonDocument {
  section_name: string;
  section_title: string;
}

export interface SectionStreamHandlers {
  onStatus?: (payload: { status: string }) => void;
  onProgress?: (payload: {
    progress?: number;
    completed?: number;
    total?: number;
    doc_type?: string;
    section_name?: string;
    message?: string;
  }) => void;
  onSectionStart?: (payload: { doc_type?: string; section_name: string; title: string }) => void;
  onSectionDelta?: (payload: { doc_type?: string; section_name: string; delta?: string; text?: string }) => void;
  onSectionDocument?: (payload: SectionDocumentPayload) => void;
  onSectionDone?: (payload: { doc_type?: string; section_name: string; completed?: number; total?: number }) => void;
  onRagStatus?: (payload: RagStatusInfo) => void;
  onAssetStatus?: (payload: AssetStatusInfo) => void;
  onCitations?: (payload: { doc_type: string; section_name?: string; citations: CitationInfo[] }) => void;
  onWarning?: (payload: { message: string; doc_type?: string; section_name?: string }) => void;
  onDocumentDone?: (payload: { message?: string; task_id?: string; document_id?: string }) => void;
  onError?: (payload: { message: string }) => void;
}

async function _consumeSse(
  streamUrl: string,
  token: string,
  eventHandler: (event: string, data: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(buildApiUrl(streamUrl), {
    headers: {
      Accept: 'text/event-stream',
      Authorization: `Bearer ${token}`,
    },
    signal,
  });

  if (!response.ok || !response.body) {
    throw new Error('Failed to open generation stream');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const segments = buffer.split('\n\n');
    buffer = segments.pop() ?? '';

    for (const segment of segments) {
      const lines = segment.split('\n');
      let eventName = '';
      let dataValue = '';

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventName = line.slice(7).trim();
        }
        if (line.startsWith('data: ')) {
          dataValue = line.slice(6).trim();
        }
      }

      if (eventName && dataValue) {
        eventHandler(eventName, dataValue);
      }
    }
  }
}

export async function consumeSectionStream(
  streamUrl: string,
  token: string,
  handlers: SectionStreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  await _consumeSse(
    streamUrl,
    token,
    (event, dataValue) => {
      const payload = JSON.parse(dataValue);

      switch (event) {
        case 'status':
          handlers.onStatus?.(payload);
          break;
        case 'progress':
          handlers.onProgress?.(payload);
          break;
        case 'section_start':
          handlers.onSectionStart?.(payload);
          break;
        case 'section_delta':
          handlers.onSectionDelta?.(payload);
          break;
        case 'section_document':
          handlers.onSectionDocument?.(payload);
          break;
        case 'section_done':
          handlers.onSectionDone?.(payload);
          break;
        case 'rag_status':
          handlers.onRagStatus?.(payload);
          break;
        case 'asset_status':
          handlers.onAssetStatus?.(payload);
          break;
        case 'citations':
          handlers.onCitations?.(payload);
          break;
        case 'warning':
          handlers.onWarning?.(payload);
          break;
        case 'document_done':
          handlers.onDocumentDone?.(payload);
          break;
        case 'error':
          handlers.onError?.(payload);
          break;
      }
    },
    signal,
  );
}
