import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';

import type {
  GenerationStartResponse,
  LessonPlanImportConfirmPayload,
  LessonPlanImportConfirmResponse,
  LessonPlanImportPreview,
  PaginatedTasks,
  TaskCreatePayload,
  TaskRecord,
  TaskUpdatePayload,
} from '@/features/task/types';
import { request } from '@/shared/api/client';

export function useTasks(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ['tasks', page, pageSize],
    queryFn: () => request<PaginatedTasks>(`/api/v1/tasks/?page=${page}&page_size=${pageSize}`),
  });
}

export function useTask(taskId: string) {
  return useQuery({
    queryKey: ['task', taskId],
    queryFn: () => request<TaskRecord>(`/api/v1/tasks/${taskId}`),
    enabled: Boolean(taskId),
  });
}

export function useCreateTaskMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TaskCreatePayload) =>
      request<TaskRecord>('/api/v1/tasks/', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['tasks'] });
      void queryClient.invalidateQueries({ queryKey: ['account', 'subscription'] });
    },
  });
}

export function useUpdateTaskMutation(taskId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TaskUpdatePayload) =>
      request<TaskRecord>(`/api/v1/tasks/${taskId}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['task', taskId] });
      void queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useDeleteTaskMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) =>
      request<void>(`/api/v1/tasks/${taskId}`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useDuplicateTaskMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) =>
      request<TaskRecord>(`/api/v1/tasks/${taskId}/duplicate`, {
        method: 'POST',
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['tasks'] });
      void queryClient.invalidateQueries({ queryKey: ['account', 'subscription'] });
    },
  });
}

export function useStartGenerationMutation(taskId: string) {
  return useMutation({
    mutationFn: (sectionId?: string) =>
      request<GenerationStartResponse>(`/api/v1/tasks/${taskId}/generate`, {
        method: 'POST',
        body: JSON.stringify(sectionId ? { section_id: sectionId } : {}),
      }),
  });
}

export function usePreviewLessonPlanImportMutation() {
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return request<LessonPlanImportPreview>('/api/v1/import/lesson-plan/preview', {
        method: 'POST',
        body: formData,
      });
    },
  });
}

export function useConfirmLessonPlanImportMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: LessonPlanImportConfirmPayload) =>
      request<LessonPlanImportConfirmResponse>('/api/v1/import/lesson-plan/confirm', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['tasks'] });
      void queryClient.invalidateQueries({ queryKey: ['account', 'subscription'] });
    },
  });
}
