import { computed, reactive } from 'vue';

export type ToastLevel = 'success' | 'info' | 'error';

export interface ToastAction {
  label: string;
  onClick?: () => void;
}

export interface ToastPayload {
  id: string;
  level: ToastLevel;
  title: string;
  description?: string;
  duration?: number;
  dismissible?: boolean;
  action?: ToastAction;
}

const toastState = reactive({
  items: [] as ToastPayload[],
});

const toastTimers = new Map<string, number>();

function clearToastTimer(id: string) {
  const timer = toastTimers.get(id);
  if (timer) {
    window.clearTimeout(timer);
    toastTimers.delete(id);
  }
}

function removeToast(id: string) {
  clearToastTimer(id);
  const index = toastState.items.findIndex((item) => item.id === id);
  if (index >= 0) {
    toastState.items.splice(index, 1);
  }
}

function pushToast(payload: Omit<ToastPayload, 'id'>) {
  const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const item: ToastPayload = {
    id,
    dismissible: true,
    duration: payload.level === 'error' ? 5400 : 3200,
    ...payload,
  };

  toastState.items.unshift(item);
  if (toastState.items.length > 4) {
    const extra = toastState.items.slice(4);
    extra.forEach((toast) => removeToast(toast.id));
    toastState.items.splice(4);
  }

  if (item.duration && item.duration > 0 && typeof window !== 'undefined') {
    const timer = window.setTimeout(() => {
      removeToast(id);
    }, item.duration);
    toastTimers.set(id, timer);
  }

  return id;
}

export function useToast() {
  return {
    toasts: computed(() => toastState.items),
    show: pushToast,
    success(title: string, description?: string) {
      return pushToast({
        level: 'success',
        title,
        description,
      });
    },
    info(title: string, description?: string) {
      return pushToast({
        level: 'info',
        title,
        description,
      });
    },
    error(title: string, description?: string) {
      return pushToast({
        level: 'error',
        title,
        description,
      });
    },
    remove: removeToast,
    clear() {
      [...toastState.items].forEach((toast) => removeToast(toast.id));
    },
  };
}
