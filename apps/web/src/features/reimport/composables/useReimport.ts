import { useMutation } from '@tanstack/vue-query';
import type { Ref } from 'vue';

import type { LessonDocument } from '@/features/editor/types';
import type { ReimportPreview } from '@/features/reimport/types';
import { request } from '@/shared/api/client';

export function usePreviewReimportMutation() {
  return useMutation({
    mutationFn: ({ documentId, file }: { documentId: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      return request<ReimportPreview>(`/api/v1/documents/${documentId}/reimport/preview`, {
        method: 'POST',
        body: formData,
      });
    },
  });
}

export function useMergeReimportMutation(documentId: Ref<string>) {
  return useMutation({
    mutationFn: ({
      file,
      sectionsToAccept,
      sectionsToReject,
      documentVersion,
    }: {
      file: File;
      sectionsToAccept: string[];
      sectionsToReject: string[];
      documentVersion: number;
    }) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('sections_to_accept', JSON.stringify(sectionsToAccept));
      formData.append('sections_to_reject', JSON.stringify(sectionsToReject));
      formData.append('document_version', String(documentVersion));
      return request<LessonDocument>(`/api/v1/documents/${documentId.value}/reimport/merge`, {
        method: 'POST',
        body: formData,
      });
    },
  });
}
