/**
 * 教案/学案内容操作工具。
 *
 * 直接操作 LessonPlanContent / StudyGuideContent 结构化模型，
 * 不再经过 block 树中间层。
 */

import type {
  AssessmentItem,
  CitationReference,
  DocumentContent,
  KeyPoints,
  LessonPlanContent,
  SectionInfo,
  SectionStatus,
  StudyGuideContent,
  TeachingObjective,
  TeachingProcessStep,
} from '@lessonpilot/shared-types';
import { isLessonPlan, isStudyGuide } from '@lessonpilot/shared-types';

// ---------------------------------------------------------------------------
// 不可变克隆
// ---------------------------------------------------------------------------

export function cloneSerializable<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

// ---------------------------------------------------------------------------
// Section 名称 → 中文标题映射
// ---------------------------------------------------------------------------

const LESSON_PLAN_SECTION_MAP: Record<string, string> = {
  objectives: '教学目标',
  key_points: '教学重难点',
  preparation: '教学准备',
  teaching_process: '教学过程',
  board_design: '板书设计',
  reflection: '教学反思',
};

const STUDY_GUIDE_SECTION_MAP: Record<string, string> = {
  learning_objectives: '学习目标',
  key_difficulties: '重点难点预测',
  prior_knowledge: '知识链接',
  self_study: '自主学习',
  collaboration: '合作探究',
  presentation: '展示提升',
  assessment: '达标测评',
  extension: '拓展延伸',
  self_reflection: '自主反思',
};

const LEARNING_PROCESS_SECTION_MAP: Record<string, keyof StudyGuideContent['learning_process']> = {
  self_study: 'selfStudy',
  collaboration: 'collaboration',
  presentation: 'presentation',
};

export function getSectionTitle(docType: string, sectionName: string): string {
  if (docType === 'study_guide') {
    return STUDY_GUIDE_SECTION_MAP[sectionName] ?? sectionName;
  }
  return LESSON_PLAN_SECTION_MAP[sectionName] ?? sectionName;
}

// ---------------------------------------------------------------------------
// 获取 Section 列表
// ---------------------------------------------------------------------------

export function getLessonPlanSections(content: LessonPlanContent): SectionInfo[] {
  return [
    { name: 'objectives', title: '教学目标', status: content.objectives_status },
    { name: 'key_points', title: '教学重难点', status: content.key_points_status },
    { name: 'preparation', title: '教学准备', status: content.preparation_status },
    { name: 'teaching_process', title: '教学过程', status: content.teaching_process_status },
    { name: 'board_design', title: '板书设计', status: content.board_design_status },
    { name: 'reflection', title: '教学反思', status: content.reflection_status },
  ];
}

export function getStudyGuideSections(content: StudyGuideContent): SectionInfo[] {
  return [
    { name: 'learning_objectives', title: '学习目标', status: content.learning_objectives_status },
    { name: 'key_difficulties', title: '重点难点预测', status: content.key_difficulties_status },
    { name: 'prior_knowledge', title: '知识链接', status: content.prior_knowledge_status },
    { name: 'self_study', title: '自主学习', status: content.self_study_status },
    { name: 'collaboration', title: '合作探究', status: content.collaboration_status },
    { name: 'presentation', title: '展示提升', status: content.presentation_status },
    { name: 'assessment', title: '达标测评', status: content.assessment_status },
    { name: 'extension', title: '拓展延伸', status: content.extension_status },
    { name: 'self_reflection', title: '自主反思', status: content.self_reflection_status },
  ];
}

export function getSections(content: DocumentContent): SectionInfo[] {
  if (isLessonPlan(content)) return getLessonPlanSections(content);
  if (isStudyGuide(content)) return getStudyGuideSections(content);
  return [];
}

// ---------------------------------------------------------------------------
// 教案 Section 操作
// ---------------------------------------------------------------------------

export type LessonPlanSectionName =
  | 'objectives'
  | 'key_points'
  | 'preparation'
  | 'teaching_process'
  | 'board_design'
  | 'reflection';

export function updateLessonPlanSection<K extends LessonPlanSectionName>(
  content: LessonPlanContent,
  section: K,
  value: LessonPlanContent[K],
): LessonPlanContent {
  return { ...content, [section]: value };
}

export function setLessonPlanSectionStatus(
  content: LessonPlanContent,
  section: LessonPlanSectionName,
  status: SectionStatus,
): LessonPlanContent {
  return { ...content, [`${section}_status`]: status };
}

export function acceptLessonPlanSection(
  content: LessonPlanContent,
  section: LessonPlanSectionName,
): LessonPlanContent {
  return setLessonPlanSectionStatus(content, section, 'confirmed');
}

// ---------------------------------------------------------------------------
// 学案 Section 操作
// ---------------------------------------------------------------------------

export type StudyGuideSectionName =
  | 'learning_objectives'
  | 'key_difficulties'
  | 'prior_knowledge'
  | 'self_study'
  | 'collaboration'
  | 'presentation'
  | 'assessment'
  | 'extension'
  | 'self_reflection';

/** Map each StudyGuide section name to its value type. */
export type StudyGuideSectionValue<K extends StudyGuideSectionName> =
  K extends 'self_study' | 'collaboration' | 'presentation' | 'assessment' | 'extension'
    ? AssessmentItem[]
    : K extends 'learning_objectives' | 'key_difficulties' | 'prior_knowledge'
      ? string[]
      : K extends 'self_reflection'
        ? string
      : never;

export function updateStudyGuideSection<K extends StudyGuideSectionName>(
  content: StudyGuideContent,
  section: K,
  value: StudyGuideSectionValue<K>,
): StudyGuideContent {
  const learningProcessSection = LEARNING_PROCESS_SECTION_MAP[section];
  if (learningProcessSection) {
    return {
      ...content,
      learning_process: {
        ...content.learning_process,
        [learningProcessSection]: value as AssessmentItem[],
      },
    };
  }
  return { ...content, [section]: value };
}

export function setStudyGuideSectionStatus(
  content: StudyGuideContent,
  section: StudyGuideSectionName,
  status: SectionStatus,
): StudyGuideContent {
  return { ...content, [`${section}_status`]: status };
}

export function acceptStudyGuideSection(
  content: StudyGuideContent,
  section: StudyGuideSectionName,
): StudyGuideContent {
  return setStudyGuideSectionStatus(content, section, 'confirmed');
}

// ---------------------------------------------------------------------------
// 通用 DocumentContent 操作
// ---------------------------------------------------------------------------

/** 更新任意 doc_type 的指定 section 内容。 */
export function updateSection<T extends DocumentContent>(
  content: T,
  sectionName: string,
  value: unknown,
): T {
  if (isStudyGuide(content)) {
    return updateStudyGuideSection(
      content,
      sectionName as StudyGuideSectionName,
      value as StudyGuideSectionValue<StudyGuideSectionName>,
    ) as T;
  }
  return updateLessonPlanSection(
    content as LessonPlanContent,
    sectionName as LessonPlanSectionName,
    value as LessonPlanContent[LessonPlanSectionName],
  ) as T;
}

/** 将指定 section 的 status 改为 confirmed。 */
export function confirmSection<T extends DocumentContent>(content: T, sectionName: string): T {
  return { ...content, [`${sectionName}_status`]: 'confirmed' } as T;
}

/** 获取所有 section 名和对应的 status。 */
export function getSectionStatuses(
  content: DocumentContent,
): Record<string, SectionStatus> {
  const result: Record<string, SectionStatus> = {};
  for (const [key, value] of Object.entries(content)) {
    if (key.endsWith('_status') && typeof value === 'string') {
      const sectionName = key.replace('_status', '');
      result[sectionName] = value as SectionStatus;
    }
  }
  return result;
}

/** 确认所有 section（将全部 pending 改为 confirmed）。 */
export function confirmAllSections<T extends DocumentContent>(content: T): T {
  const updated = { ...content } as Record<string, unknown>;
  for (const key of Object.keys(updated)) {
    if (key.endsWith('_status') && updated[key] === 'pending') {
      updated[key] = 'confirmed';
    }
  }
  return updated as T;
}

/** 获取 confirmed 内容（将所有 pending section 置为 confirmed）。 */
export function getConfirmedContent<T extends DocumentContent>(content: T): T {
  return confirmAllSections(content);
}

// ---------------------------------------------------------------------------
// Section 内容访问工具
// ---------------------------------------------------------------------------

/** 获取教案某个 section 的内容（类型安全）。 */
export function getLessonPlanSectionContent(
  content: LessonPlanContent,
  name: LessonPlanSectionName,
): TeachingObjective[] | KeyPoints | string[] | TeachingProcessStep[] | string {
  return content[name];
}

/** 获取学案某个 section 的内容（类型安全）。 */
export function getStudyGuideSectionContent(
  content: StudyGuideContent,
  name: StudyGuideSectionName,
): unknown {
  const learningProcessSection = LEARNING_PROCESS_SECTION_MAP[name];
  if (learningProcessSection) return content.learning_process[learningProcessSection];
  return content[name as keyof StudyGuideContent];
}

export function getSectionContent(content: DocumentContent, sectionName: string): unknown {
  if (isStudyGuide(content)) {
    return getStudyGuideSectionContent(content, sectionName as StudyGuideSectionName);
  }
  return getLessonPlanSectionContent(content as LessonPlanContent, sectionName as LessonPlanSectionName);
}

export function getSectionReferences(
  content: DocumentContent,
  sectionName: string,
): CitationReference[] {
  return content.section_references?.[sectionName] ?? [];
}
