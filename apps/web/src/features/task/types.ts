export interface TaskRecord {
  id: string;
  title: string;
  subject: string;
  grade: string;
  topic: string;
  requirements: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedTasks {
  items: TaskRecord[];
  page: number;
  page_size: number;
  total: number;
}

export interface TaskCreatePayload {
  subject: string;
  grade: string;
  topic: string;
  requirements?: string | null;
  title?: string | null;
}

export interface TaskUpdatePayload {
  title?: string | null;
  requirements?: string | null;
  status?: string | null;
}

export interface GenerationStartResponse {
  stream_url: string;
}

