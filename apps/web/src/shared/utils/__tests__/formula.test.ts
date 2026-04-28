import { describe, expect, it } from 'vitest';

import { containsFormula, parseFormulaSegments, repairLatexText } from '../formula';

describe('formula utilities', () => {
  it('detects inline and display formulas', () => {
    expect(containsFormula('由 \\(a^2+b^2=c^2\\) 得出结论')).toBe(true);
    expect(containsFormula('$$S=\\frac{1}{2}ah$$')).toBe(true);
    expect(containsFormula('普通教学目标')).toBe(false);
  });

  it('renders formula segments with KaTeX html', () => {
    const segments = parseFormulaSegments('公式：\\(S=\\frac{1}{2}ah\\)');

    expect(segments).toHaveLength(2);
    expect(segments[1]).toMatchObject({ kind: 'math', content: 'S=\\frac{1}{2}ah' });
    expect(segments[1].kind === 'math' ? segments[1].html : '').toContain('katex');
  });

  it('repairs common JSON-damaged LaTeX escapes', () => {
    const repaired = repairLatexText('公式：\\(S=\x0crac{1}{2}ah\\)，角度 \theta');

    expect(repaired).toContain('\\frac{1}{2}');
    expect(repaired).toContain('\\theta');
  });
});
