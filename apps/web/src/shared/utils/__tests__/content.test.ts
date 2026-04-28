import { describe, expect, it } from 'vitest';

import type {
  LessonPlanContent,
  StudyGuideContent,
} from '@lessonpilot/shared-types';

import {
  acceptLessonPlanSection,
  acceptStudyGuideSection,
  cloneSerializable,
  confirmAllSections,
  confirmSection,
  getSectionStatuses,
  getSectionTitle,
  getSections,
  getStudyGuideSectionContent,
  setLessonPlanSectionStatus,
  updateLessonPlanSection,
  updateSection,
  updateStudyGuideSection,
} from '../content';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function makeLessonPlan(overrides: Partial<LessonPlanContent> = {}): LessonPlanContent {
  return {
    doc_type: 'lesson_plan',
    header: {
      title: '春',
      subject: '语文',
      grade: '七年级',
      classHour: 1,
      lessonCategory: 'new',
      teacher: '',
    },
    objectives: [],
    objectives_status: 'pending',
    key_points: { keyPoints: [], difficulties: [] },
    key_points_status: 'pending',
    preparation: [],
    preparation_status: 'pending',
    teaching_process: [],
    teaching_process_status: 'pending',
    board_design: '',
    board_design_status: 'pending',
    reflection: '',
    reflection_status: 'pending',
    section_references: {},
    ...overrides,
  };
}

function makeStudyGuide(overrides: Partial<StudyGuideContent> = {}): StudyGuideContent {
  return {
    doc_type: 'study_guide',
    header: {
      title: '春',
      subject: '语文',
      grade: '七年级',
      className: '',
      studentName: '',
      date: '',
    },
    learning_objectives: [],
    learning_objectives_status: 'pending',
    key_difficulties: [],
    key_difficulties_status: 'pending',
    prior_knowledge: [],
    prior_knowledge_status: 'pending',
    learning_process: { selfStudy: [], collaboration: [], presentation: [] },
    self_study_status: 'pending',
    collaboration_status: 'pending',
    presentation_status: 'pending',
    assessment: [],
    assessment_status: 'pending',
    extension: [],
    extension_status: 'pending',
    self_reflection: '',
    self_reflection_status: 'pending',
    section_references: {},
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('cloneSerializable', () => {
  it('returns a deep copy', () => {
    const original = { a: [1, 2], b: 'x' };
    const cloned = cloneSerializable(original);
    expect(cloned).toEqual(original);
    expect(cloned).not.toBe(original);
    expect(cloned.a).not.toBe(original.a);
  });
});

describe('getSectionTitle', () => {
  it('returns Chinese title for lesson plan section', () => {
    expect(getSectionTitle('lesson_plan', 'objectives')).toBe('教学目标');
  });

  it('returns Chinese title for study guide section', () => {
    expect(getSectionTitle('study_guide', 'learning_objectives')).toBe('学习目标');
  });

  it('returns raw name for unknown section', () => {
    expect(getSectionTitle('lesson_plan', 'unknown_section')).toBe('unknown_section');
  });
});

describe('getSections', () => {
  it('returns 6 sections for lesson plan', () => {
    const sections = getSections(makeLessonPlan());
    expect(sections).toHaveLength(6);
    expect(sections[0]).toEqual({ name: 'objectives', title: '教学目标', status: 'pending' });
  });

  it('returns 9 sections for study guide', () => {
    const sections = getSections(makeStudyGuide());
    expect(sections).toHaveLength(9);
    expect(sections[0]).toEqual({ name: 'learning_objectives', title: '学习目标', status: 'pending' });
  });
});

describe('updateLessonPlanSection', () => {
  it('updates objectives immutably', () => {
    const original = makeLessonPlan();
    const newObjectives = [{ dimension: 'knowledge' as const, content: 'test' }];
    const updated = updateLessonPlanSection(original, 'objectives', newObjectives);
    expect(updated.objectives).toEqual(newObjectives);
    expect(original.objectives).toEqual([]);
  });
});

describe('setLessonPlanSectionStatus', () => {
  it('sets status immutably', () => {
    const original = makeLessonPlan();
    const updated = setLessonPlanSectionStatus(original, 'objectives', 'confirmed');
    expect(updated.objectives_status).toBe('confirmed');
    expect(original.objectives_status).toBe('pending');
  });
});

describe('acceptLessonPlanSection', () => {
  it('confirms a section', () => {
    const original = makeLessonPlan({ objectives_status: 'pending' });
    const updated = acceptLessonPlanSection(original, 'objectives');
    expect(updated.objectives_status).toBe('confirmed');
  });
});

describe('updateStudyGuideSection', () => {
  it('updates learning_objectives immutably', () => {
    const original = makeStudyGuide();
    const updated = updateStudyGuideSection(original, 'learning_objectives', ['目标1']);
    expect(updated.learning_objectives).toEqual(['目标1']);
    expect(original.learning_objectives).toEqual([]);
  });

  it('updates self_study through learning_process', () => {
    const original = makeStudyGuide();
    const items = [{ level: 'A' as const, itemType: 'short_answer' as const, prompt: '题目', options: [], answer: '', analysis: '' }];
    const updated = updateStudyGuideSection(original, 'self_study', items);
    expect(updated.learning_process.selfStudy).toEqual(items);
    expect(original.learning_process.selfStudy).toEqual([]);
  });
});

describe('acceptStudyGuideSection', () => {
  it('confirms a section', () => {
    const original = makeStudyGuide({ learning_objectives_status: 'pending' });
    const updated = acceptStudyGuideSection(original, 'learning_objectives');
    expect(updated.learning_objectives_status).toBe('confirmed');
  });
});

describe('updateSection', () => {
  it('updates a generic section immutably', () => {
    const original = makeLessonPlan();
    const updated = updateSection(original, 'reflection', '新的反思内容');
    expect(updated.reflection).toBe('新的反思内容');
    expect(original.reflection).toBe('');
  });

  it('routes study guide self_study to learning_process', () => {
    const items = [{ level: 'A' as const, itemType: 'choice' as const, prompt: 'q', options: [], answer: 'a', analysis: '' }];
    const original = makeStudyGuide();
    const updated = updateSection(original, 'self_study', items);
    expect(updated.learning_process.selfStudy).toEqual(items);
    expect((updated as StudyGuideContent & { self_study?: unknown }).self_study).toBeUndefined();
  });
});

describe('confirmSection', () => {
  it('confirms a section by name', () => {
    const original = makeLessonPlan();
    const updated = confirmSection(original, 'objectives');
    expect(updated.objectives_status).toBe('confirmed');
    expect(original.objectives_status).toBe('pending');
  });
});

describe('getSectionStatuses', () => {
  it('extracts all section statuses', () => {
    const content = makeLessonPlan({
      objectives_status: 'confirmed',
      key_points_status: 'pending',
    });
    const statuses = getSectionStatuses(content);
    expect(statuses.objectives).toBe('confirmed');
    expect(statuses.key_points).toBe('pending');
    expect(Object.keys(statuses)).toHaveLength(6);
  });
});

describe('confirmAllSections', () => {
  it('converts all pending to confirmed', () => {
    const content = makeLessonPlan({
      objectives_status: 'confirmed',
      key_points_status: 'pending',
    });
    const updated = confirmAllSections(content);
    expect(updated.objectives_status).toBe('confirmed');
    expect(updated.key_points_status).toBe('confirmed');
  });

  it('does not mutate original', () => {
    const original = makeLessonPlan();
    confirmAllSections(original);
    expect(original.key_points_status).toBe('pending');
  });
});

describe('getStudyGuideSectionContent', () => {
  it('returns self_study from learning_process', () => {
    const items = [{ level: 'A' as const, itemType: 'choice' as const, prompt: 'q', options: [], answer: 'a', analysis: '' }];
    const content = makeStudyGuide({
      learning_process: { selfStudy: items, collaboration: [], presentation: [] },
    });
    expect(getStudyGuideSectionContent(content, 'self_study')).toEqual(items);
  });

  it('returns top-level section for learning_objectives', () => {
    const content = makeStudyGuide({ learning_objectives: ['obj1'] });
    expect(getStudyGuideSectionContent(content, 'learning_objectives')).toEqual(['obj1']);
  });
});
