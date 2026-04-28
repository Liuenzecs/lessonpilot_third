import katex from 'katex';

export type FormulaSegment =
  | { kind: 'text'; content: string }
  | { kind: 'math'; content: string; displayMode: boolean; html: string };

const DELIMITERS = [
  { open: '$$', close: '$$', displayMode: true },
  { open: '\\[', close: '\\]', displayMode: true },
  { open: '\\(', close: '\\)', displayMode: false },
] as const;

const CONTROL_REPAIRS: Array<[string, string]> = [
  ['\x0crac', '\\frac'],
  ['\x0cbox', '\\fbox'],
  ['\times', '\\times'],
  ['\theta', '\\theta'],
  ['\tfrac', '\\tfrac'],
  ['\text', '\\text'],
  ['\tan', '\\tan'],
  ['\to', '\\to'],
  ['\beta', '\\beta'],
  ['\begin', '\\begin'],
  ['\rho', '\\rho'],
  ['\right', '\\right'],
  ['\nabla', '\\nabla'],
];

export function repairLatexText(value: string): string {
  return CONTROL_REPAIRS.reduce(
    (text, [broken, fixed]) => text.replaceAll(broken, fixed),
    value,
  );
}

export function containsFormula(value: string): boolean {
  const text = repairLatexText(value);
  return DELIMITERS.some(({ open, close }) => text.includes(open) && text.includes(close));
}

export function renderFormula(content: string, displayMode: boolean): string {
  return katex.renderToString(content, {
    displayMode,
    output: 'html',
    strict: false,
    throwOnError: false,
    trust: false,
  });
}

function findNextDelimiter(text: string, fromIndex: number) {
  let match: { index: number; delimiter: (typeof DELIMITERS)[number] } | null = null;

  for (const delimiter of DELIMITERS) {
    const index = text.indexOf(delimiter.open, fromIndex);
    if (index !== -1 && (!match || index < match.index)) {
      match = { index, delimiter };
    }
  }

  return match;
}

export function parseFormulaSegments(value: string): FormulaSegment[] {
  const text = repairLatexText(value);
  const segments: FormulaSegment[] = [];
  let cursor = 0;

  while (cursor < text.length) {
    const match = findNextDelimiter(text, cursor);
    if (!match) {
      segments.push({ kind: 'text', content: text.slice(cursor) });
      break;
    }

    if (match.index > cursor) {
      segments.push({ kind: 'text', content: text.slice(cursor, match.index) });
    }

    const mathStart = match.index + match.delimiter.open.length;
    const mathEnd = text.indexOf(match.delimiter.close, mathStart);
    if (mathEnd === -1) {
      segments.push({ kind: 'text', content: text.slice(match.index) });
      break;
    }

    const content = text.slice(mathStart, mathEnd).trim();
    if (content) {
      segments.push({
        kind: 'math',
        content,
        displayMode: match.delimiter.displayMode,
        html: renderFormula(content, match.delimiter.displayMode),
      });
    }
    cursor = mathEnd + match.delimiter.close.length;
  }

  return segments;
}
