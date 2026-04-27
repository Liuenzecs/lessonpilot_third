import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';

import type {
  GenerationStartResponse,
  LessonPlanImportConfirmPayload,
  LessonPlanImportConfirmResponse,
  LessonPlanImportPreview,
  PaginatedTasks,
  PersonalAssetConfirmPayload,
  PersonalAssetPreview,
  PersonalAssetRecord,
  SchoolTemplateConfirmPayload,
  SchoolTemplatePreview,
  TaskCreatePayload,
  TaskRecord,
  TaskUpdatePayload,
  TemplateRecord,
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

export function useSchoolTemplates() {
  return useQuery({
    queryKey: ['school-templates'],
    queryFn: () => request<TemplateRecord[]>('/api/v1/templates/school/personal'),
  });
}

export function usePreviewSchoolTemplateMutation() {
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return request<SchoolTemplatePreview>('/api/v1/templates/school/preview', {
        method: 'POST',
        body: formData,
      });
    },
  });
}

export function useConfirmSchoolTemplateMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SchoolTemplateConfirmPayload) =>
      request<TemplateRecord>('/api/v1/templates/school/confirm', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['school-templates'] });
    },
  });
}

export function useDeleteSchoolTemplateMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (templateId: string) =>
      request<void>(`/api/v1/templates/school/${templateId}`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['school-templates'] });
    },
  });
}

export function usePersonalAssets() {
  return useQuery({
    queryKey: ['personal-assets'],
    queryFn: () => request<PersonalAssetRecord[]>('/api/v1/personal-assets/'),
  });
}

export function usePreviewPersonalAssetMutation() {
  return useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return request<PersonalAssetPreview>('/api/v1/personal-assets/preview', {
        method: 'POST',
        body: formData,
      });
    },
  });
}

export function useConfirmPersonalAssetMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: PersonalAssetConfirmPayload) =>
      request<PersonalAssetRecord>('/api/v1/personal-assets/confirm', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['personal-assets'] });
    },
  });
}

export function useDeletePersonalAssetMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (assetId: string) =>
      request<void>(`/api/v1/personal-assets/${assetId}`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['personal-assets'] });
    },
  });
}
