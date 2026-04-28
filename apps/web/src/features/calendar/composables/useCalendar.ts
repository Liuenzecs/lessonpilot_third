import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query';
import type { Ref } from 'vue';

import type {
  LessonScheduleEntryCreate,
  LessonScheduleEntryRead,
  SemesterCreate,
  SemesterDetailRead,
  SemesterRead,
  SemesterUpdate,
} from '@/features/calendar/types';
import { request } from '@/shared/api/client';

export function useSemesters() {
  return useQuery({
    queryKey: ['semesters'],
    queryFn: () => request<SemesterRead[]>('/api/v1/calendar/semesters'),
  });
}

export function useSemesterDetail(semesterId: Ref<string | null>, enabled: Ref<boolean>) {
  return useQuery({
    queryKey: ['semester-detail', semesterId],
    queryFn: () => request<SemesterDetailRead>(`/api/v1/calendar/semesters/${semesterId.value}`),
    enabled,
  });
}

export function useCreateSemesterMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SemesterCreate) =>
      request<SemesterRead>('/api/v1/calendar/semesters', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['semesters'] });
    },
  });
}

export function useDeleteSemesterMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (semesterId: string) =>
      request<void>(`/api/v1/calendar/semesters/${semesterId}`, { method: 'DELETE' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['semesters'] });
    },
  });
}

export function useUpdateSemesterMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ semesterId, payload }: { semesterId: string; payload: SemesterUpdate }) =>
      request<SemesterRead>(`/api/v1/calendar/semesters/${semesterId}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['semesters'] });
    },
  });
}

export function useAddEntryMutation(semesterId: Ref<string | null>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ weekId, payload }: { weekId: string; payload: LessonScheduleEntryCreate }) =>
      request<LessonScheduleEntryRead>(`/api/v1/calendar/weeks/${weekId}/entries`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['semester-detail', semesterId.value] });
    },
  });
}

export function useDeleteEntryMutation(semesterId: Ref<string | null>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (entryId: string) =>
      request<void>(`/api/v1/calendar/entries/${entryId}`, { method: 'DELETE' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['semester-detail', semesterId.value] });
    },
  });
}
