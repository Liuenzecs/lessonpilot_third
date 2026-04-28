export interface ShareLinkCreate {
  permission: 'read' | 'comment';
  expires_in_days?: number | null;
}

export interface ShareLinkRead {
  id: string;
  document_id: string;
  token: string;
  permission: string;
  expires_at: string | null;
  is_active: boolean;
  url: string;
  created_at: string;
}

export interface ShareLinkUpdate {
  is_active?: boolean | null;
  permission?: 'read' | 'comment' | null;
  expires_in_days?: number | null;
}

export interface ShareCommentCreate {
  section_name?: string | null;
  body: string;
  author_name?: string;
}

export interface ShareCommentRead {
  id: string;
  section_name: string | null;
  body: string;
  author_name: string;
  resolved: boolean;
  created_at: string;
}

export interface SharedDocumentView {
  title: string;
  subject: string;
  grade: string;
  topic: string;
  doc_type: string;
  content: Record<string, unknown>;
  permission: string;
  comments: ShareCommentRead[];
}
