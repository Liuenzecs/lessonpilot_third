import { useAuthStore } from '@/app/stores/auth';

function getAdminAllowlist(): string[] {
  return (import.meta.env.VITE_ADMIN_ALLOWLIST_EMAILS || '')
    .split(',')
    .map((email) => email.trim().toLowerCase())
    .filter(Boolean);
}

export function useAdminAccess() {
  const authStore = useAuthStore();
  const userEmail = authStore.user?.email?.trim().toLowerCase() || '';
  return {
    isAdmin: getAdminAllowlist().includes(userEmail),
  };
}
