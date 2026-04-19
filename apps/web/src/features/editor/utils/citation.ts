import type { CitationInfo } from '@/features/generation/composables/useGeneration'

const CITE_RE = /\[cite:([a-f0-9\-]+)\]/g

/** 从文本中提取所有 chunk_id */
export function extractCitationIds(text: string): string[] {
  const ids: string[] = []
  let match: RegExpExecArray | null
  const re = new RegExp(CITE_RE)
  while ((match = re.exec(text)) !== null) {
    ids.push(match[1])
  }
  return ids
}

/** 将 [cite:xxx] 替换为带 data 属性的 <sup> 标签，返回 HTML 字符串 */
export function renderCitedText(
  text: string,
  citations: Record<string, CitationInfo>,
): string {
  return text.replace(
    CITE_RE,
    (_match, chunkId: string) => {
      const c = citations[chunkId]
      if (!c) return ''
      const label = escapeHtml(c.source)
      const title = escapeHtml(c.title)
      const snippet = escapeHtml(c.content_snippet)
      return `<sup class="cite-label" data-id="${chunkId}" data-source="${label}" data-title="${title}" data-snippet="${snippet}">[${label}]</sup>`
    },
  )
}

/** 清除文本中的 [cite:xxx] 标记 */
export function stripCitations(text: string): string {
  return text.replace(CITE_RE, '')
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
