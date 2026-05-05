/** 前端埋点客户端 — 批量发送用户行为事件到服务端。 */

import { request } from './client';

interface AnalyticsPayload {
  event_name: string;
  source?: string;
  user_id?: string | null;
  anonymous_id?: string | null;
  session_id: string;
  page_path: string;
  referrer?: string | null;
  properties?: Record<string, unknown>;
  client_event_id?: string | null;
}

function generateSessionId(): string {
  const stored = sessionStorage.getItem('analytics_session_id');
  if (stored) return stored;
  const id = crypto.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  sessionStorage.setItem('analytics_session_id', id);
  return id;
}

function generateEventId(): string {
  return crypto.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

let _batch: AnalyticsPayload[] = [];
let _flushTimer: ReturnType<typeof setTimeout> | null = null;
const FLUSH_INTERVAL = 5000;
const MAX_BATCH_SIZE = 20;
let _userId: string | null = null;

export function setAnalyticsUserId(userId: string | null) {
  _userId = userId;
}

function flush() {
  if (_flushTimer) {
    clearTimeout(_flushTimer);
    _flushTimer = null;
  }
  if (_batch.length === 0) return;

  const events = [..._batch];
  _batch = [];

  request('/api/v1/analytics/events', {
    method: 'POST',
    body: JSON.stringify(events),
  }).catch(() => {
    // Silent fail — analytics should never break the user experience
  });
}

export function track(
  eventName: string,
  properties?: Record<string, unknown>,
) {
  const event: AnalyticsPayload = {
    event_name: eventName,
    source: 'web',
    user_id: _userId,
    session_id: generateSessionId(),
    page_path: window.location.pathname,
    referrer: document.referrer || null,
    properties: properties ?? {},
    client_event_id: generateEventId(),
  };

  _batch.push(event);

  if (_batch.length >= MAX_BATCH_SIZE) {
    flush();
  } else if (!_flushTimer) {
    _flushTimer = setTimeout(flush, FLUSH_INTERVAL);
  }
}
