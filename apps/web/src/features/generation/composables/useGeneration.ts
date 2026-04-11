import { buildApiUrl } from '@/shared/api/client';

export interface GenerationEventHandlers {
  onEvent: (event: string, payload: unknown) => void;
}

export async function consumeGenerationStream(
  streamUrl: string,
  token: string,
  handlers: GenerationEventHandlers,
): Promise<void> {
  const response = await fetch(buildApiUrl(streamUrl), {
    headers: {
      Accept: 'text/event-stream',
      Authorization: `Bearer ${token}`,
    },
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
        handlers.onEvent(eventName, JSON.parse(dataValue));
      }
    }
  }
}

