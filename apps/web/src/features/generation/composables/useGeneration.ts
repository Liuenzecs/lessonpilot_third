import { buildApiUrl } from '@/shared/api/client';

// ---------------------------------------------------------------------------
// 流式生成事件 handlers（Sprint 3 新协议）
// ---------------------------------------------------------------------------

export interface StreamingEventHandlers {
  onStatus: (payload: { status: string }) => void;
  onProgress: (payload: { progress: number; message: string; doc_type?: string }) => void;
  onSectionStart: (payload: { doc_type: string; section_name: string; title: string }) => void;
  onSectionDelta: (payload: { text: string }) => void;
  onSectionComplete: (payload: { doc_type: string; section_name: string }) => void;
  onDocument: (payload: { id: string; doc_type: string; content: unknown; version: number }) => void;
  onDone: (payload: { message: string }) => void;
  onError: (payload: { message: string }) => void;
}

// ---------------------------------------------------------------------------
// 旧版通用 handler（rewrite / append 仍在使用）
// ---------------------------------------------------------------------------

export interface GenerationEventHandlers {
  onEvent: (event: string, payload: unknown) => void;
}

// ---------------------------------------------------------------------------
// 内部 SSE 消费
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// 流式生成消费（Sprint 3 新协议）
// ---------------------------------------------------------------------------

export async function consumeGenerationStream(
  streamUrl: string,
  token: string,
  handlers: StreamingEventHandlers,
  signal?: AbortSignal,
): Promise<void> {
  await _consumeSse(
    streamUrl,
    token,
    (event, dataValue) => {
      const payload = JSON.parse(dataValue);

      switch (event) {
        case 'status':
          handlers.onStatus(payload);
          break;
        case 'progress':
          handlers.onProgress(payload);
          break;
        case 'section_start':
          handlers.onSectionStart(payload);
          break;
        case 'section_delta':
          handlers.onSectionDelta(payload);
          break;
        case 'section_complete':
          handlers.onSectionComplete(payload);
          break;
        case 'document':
          handlers.onDocument(payload);
          break;
        case 'done':
          handlers.onDone(payload);
          break;
        case 'error':
          handlers.onError(payload);
          break;
      }
    },
    signal,
  );
}

// ---------------------------------------------------------------------------
// 旧版 Rewrite / Append 消费（保留不动）
// ---------------------------------------------------------------------------

export async function consumeRewriteStream(
  streamUrl: string,
  token: string,
  handlers: GenerationEventHandlers,
): Promise<void> {
  await _consumeSse(streamUrl, token, (event, dataValue) => {
    handlers.onEvent(event, JSON.parse(dataValue));
  });
}

export async function consumeAppendStream(
  streamUrl: string,
  token: string,
  handlers: GenerationEventHandlers,
): Promise<void> {
  await _consumeSse(streamUrl, token, (event, dataValue) => {
    handlers.onEvent(event, JSON.parse(dataValue));
  });
}
