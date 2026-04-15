import { download } from '@/shared/api/client';

/** 导出单个文档为 Word 文件。 */
export async function exportDocx(documentId: string, title: string): Promise<void> {
  const blob = await download(`/api/v1/documents/${documentId}/export?format=docx`);
  triggerDownload(blob, `${title}.docx`);
}

/** 依次导出多个文档。 */
export async function exportMultipleDocx(
  items: Array<{ documentId: string; title: string }>,
): Promise<void> {
  for (const item of items) {
    await exportDocx(item.documentId, item.title);
  }
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
