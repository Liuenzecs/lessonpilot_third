import type { App } from 'vue';
import type { Router } from 'vue-router';

function scrubEventPayload(payload: unknown): unknown {
  if (Array.isArray(payload)) {
    return payload.map(scrubEventPayload);
  }
  if (payload && typeof payload === 'object') {
    return Object.fromEntries(
      Object.entries(payload).map(([key, value]) => {
        const lowered = key.toLowerCase();
        if (
          ['authorization', 'password', 'token', 'content', 'prompt', 'secret', 'jwt'].some((token) =>
            lowered.includes(token),
          )
        ) {
          return [key, '[Filtered]'];
        }
        return [key, scrubEventPayload(value)];
      }),
    );
  }
  return payload;
}

function getSampleRate(): number {
  const raw = Number(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || '0');
  return Number.isFinite(raw) ? raw : 0;
}

export async function initBrowserSentry(app: App, router: Router) {
  const dsn = import.meta.env.VITE_SENTRY_DSN_WEB;
  if (!dsn) {
    return;
  }

  const Sentry = await import('@sentry/vue');
  Sentry.init({
    app,
    dsn,
    environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || 'development',
    integrations: [Sentry.browserTracingIntegration({ router })],
    tracesSampleRate: getSampleRate(),
    beforeSend(event) {
      return scrubEventPayload(event) as typeof event;
    },
    sendDefaultPii: false,
  });
}
