/** 班级组 composable — TanStack Query hooks。 */
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/vue-query';

import { request } from '@/shared/api/client';

export interface ClassGroup {
  id: string;
  user_id: string;
  name: string;
  level: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ClassGroupCreate {
  name: string;
  level?: string;
  notes?: string | null;
}

export interface ClassGroupUpdate {
  name?: string;
  level?: string;
  notes?: string | null;
}

export interface CreateVariantPayload {
  class_group_id: string;
  differentiation_level?: string;
}

export interface VariantTask {
  id: string;
  title: string;
  status: string;
  class_group_id: string | null;
  base_task_id: string | null;
  subject: string;
  grade: string;
  topic: string;
  created_at: string;
}

export function useClassGroups() {
  return useQuery({
    queryKey: ['class-groups'],
    queryFn: () => request<ClassGroup[]>('/api/v1/class-groups'),
    staleTime: 60000,
  });
}

export function useCreateClassGroupMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ClassGroupCreate) =>
      request<ClassGroup>('/api/v1/class-groups', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['class-groups'] });
    },
  });
}

export function useUpdateClassGroupMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }: ClassGroupUpdate & { id: string }) =>
      request<ClassGroup>(`/api/v1/class-groups/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['class-groups'] });
    },
  });
}

export function useDeleteClassGroupMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      request<void>(`/api/v1/class-groups/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['class-groups'] });
    },
  });
}

export function useTaskVariants(taskId: string) {
  return useQuery({
    queryKey: ['task-variants', taskId],
    queryFn: () =>
      request<VariantTask[]>(`/api/v1/class-groups/tasks/${taskId}/variants`),
    enabled: Boolean(taskId),
    staleTime: 30000,
  });
}

export function useCreateVariantMutation(taskId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateVariantPayload) =>
      request<VariantTask>(`/api/v1/class-groups/tasks/${taskId}/variants`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['task-variants', taskId] });
      void queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}
