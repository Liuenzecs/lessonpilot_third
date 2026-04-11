import { download } from '@/shared/api/client';

export async function exportDocx(documentId: string, title: string): Promise<void> {
  const blob = await download(`/api/v1/documents/${documentId}/export?format=docx`);
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${title}.docx`;
  anchor.click();
  URL.revokeObjectURL(url);
}

export async function exportPdf(documentId: string, title: string): Promise<void> {
  const blob = await download(`/api/v1/documents/${documentId}/export?format=pdf`);
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${title}.pdf`;
  anchor.click();
  URL.revokeObjectURL(url);
}
