export interface DiffSegment {
  type: 'equal' | 'insert' | 'delete';
  text: string;
}

export interface SectionDiff {
  section_name: string;
  section_title: string;
  status: 'unchanged' | 'modified' | 'new' | 'deleted';
  original_content: unknown;
  imported_content: unknown;
  diff_segments: DiffSegment[] | null;
}

export interface ReimportPreview {
  source_filename: string;
  original_document_id: string;
  original_version: number;
  sections: SectionDiff[];
}
