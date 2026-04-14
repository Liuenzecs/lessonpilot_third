import createDOMPurify from 'dompurify';

const ALLOWED_TAGS = ['p', 'br', 'strong', 'b', 'em', 'i', 'u', 'ul', 'ol', 'li', 'code', 'a'];
const ALLOWED_ATTR = ['href', 'target', 'rel'];

let purifier: ReturnType<typeof createDOMPurify> | null = null;

function getPurifier() {
  if (typeof window === 'undefined') {
    return null;
  }
  if (!purifier) {
    purifier = createDOMPurify(window);
  }
  return purifier;
}

export function sanitizeRichHtml(value: string): string {
  if (!value) {
    return '';
  }

  const domPurify = getPurifier();
  if (!domPurify) {
    return value.replace(/<[^>]+>/g, ' ');
  }

  return domPurify.sanitize(value, {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
    ALLOW_DATA_ATTR: false,
    FORBID_ATTR: ['style'],
    ALLOWED_URI_REGEXP: /^(?:(?:https?:|mailto:|tel:)|[^a-z]|[a-z+.-]+(?:[^a-z+.-:]|$))/i,
  });
}
