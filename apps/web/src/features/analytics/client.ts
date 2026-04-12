import type { Pinia } from 'pinia';
import type { Router } from 'vue-router';

import { useAuthStore } from '@/app/stores/auth';
import { buildApiUrl } from '@/shared/api/client';

interface AnalyticsQueueEvent {
  event_name: string;
  occurred_at: string;
  source: 'client';
  anonymous_id?: string;
  session_id: string;
  page_path: string;
  referrer?: string;
  properties: Record<string, unknown>;
  client_event_id: string;
}

const ANALYTICS_QUEUE_LIMIT = 20;
const ANALYTICS_FLUSH_DELAY = 1200;
const ANON_STORAGE_KEY = 'lessonpilot.analytics.anonymous_id';
const SESSION_STORAGE_KEY = 'lessonpilot.analytics.session_id';

let queue: AnalyticsQueueEvent[] = [];
let flushTimer: number | null = null;

function canUseBrowserApis(): boolean {
  return typeof window !== 'undefined' && typeof localStorage !== 'undefined' && typeof fetch !== 'undefined';
}

function readOrCreateStorageValue(storageKey: string): string {
  if (!canUseBrowserApis()) {
    return crypto.randomUUID();
  }
  const storage = storageKey === SESSION_STORAGE_KEY ? sessionStorage : localStorage;
  const existing = storage.getItem(storageKey);
  if (existing) {
    return existing;
  }
  const next = crypto.randomUUID();
  storage.setItem(storageKey, next);
  return next;
}

function getSessionId(): string {
  return readOrCreateStorageValue(SESSION_STORAGE_KEY);
}

function getAnonymousId(pinia: Pinia): string | undefined {
  const authStore = useAuthStore(pinia);
  if (authStore.isAuthenticated) {
    return undefined;
  }
  return readOrCreateStorageValue(ANON_STORAGE_KEY);
}

function getAccessToken(): string | null {
  if (!canUseBrowserApis()) {
    return null;
  }

  try {
    const raw = localStorage.getItem('lessonpilot.auth');
    if (!raw) {
      return null;
    }
    return (JSON.parse(raw) as { token?: string | null }).token ?? null;
  } catch {
    return null;
  }
}

function scheduleFlush() {
  if (!canUseBrowserApis() || flushTimer !== null) {
    return;
  }

  flushTimer = window.setTimeout(() => {
    flushTimer = null;
    void flushAnalyticsQueue();
  }, ANALYTICS_FLUSH_DELAY);
}

export async function flushAnalyticsQueue() {
  if (!canUseBrowserApis() || queue.length === 0) {
    return;
  }

  const payload = { events: queue.slice(0, ANALYTICS_QUEUE_LIMIT) };
  queue = queue.slice(payload.events.length);

  try {
    const token = getAccessToken();
    await fetch(buildApiUrl('/api/v1/analytics/events/batch'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
      keepalive: true,
    });
  } catch {
    queue = [...payload.events, ...queue].slice(0, ANALYTICS_QUEUE_LIMIT * 4);
  }
}

export function trackClientEvent(
  pinia: Pinia,
  eventName: string,
  pagePath: string,
  properties: Record<string, unknown> = {},
) {
  if (!canUseBrowserApis()) {
    return;
  }

  queue.push({
    event_name: eventName,
    occurred_at: new Date().toISOString(),
    source: 'client',
    anonymous_id: getAnonymousId(pinia),
    session_id: getSessionId(),
    page_path: pagePath,
    referrer: document.referrer || undefined,
    properties,
    client_event_id: crypto.randomUUID(),
  });

  if (queue.length >= ANALYTICS_QUEUE_LIMIT) {
    void flushAnalyticsQueue();
    return;
  }
  scheduleFlush();
}

export function installAnalytics(router: Router, pinia: Pinia) {
  if (!canUseBrowserApis()) {
    return;
  }

  router.afterEach((to) => {
    trackClientEvent(pinia, 'page_view', to.fullPath, {
      route_name: String(to.name || ''),
      layout: to.meta.requiresAuth ? 'private' : 'public',
    });
  });

  window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      void flushAnalyticsQueue();
    }
  });
}

export function createCtaTracker(pinia: Pinia, pagePath: string, ctaId: string, location: string) {
  return () => trackClientEvent(pinia, 'cta_click', pagePath, { cta_id: ctaId, location });
}
