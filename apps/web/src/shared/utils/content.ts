/**
 * 教案/学案内容操作工具。
 *
 * 当前提供 section 级操作（教案/学案新模型）和 block 系统兼容 stub。
 * Sprint 4 编辑器重写时会扩展/替换这些工具。
 */

import type {
  AssessmentItem,
  Block,
  BlockType,
  ContentDocument,
  DocumentContent,
  KeyPoints,
  LessonPlanContent,
  LearningProcess,
  SectionBlock,
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
// 类型兼容（旧代码过渡期）
// ---------------------------------------------------------------------------

/** 旧的 InsertableBlockType 类型 — 过渡期兼容。 */
export type InsertableBlockType = string;
/** 旧的 ContainerBlock 类型 — 过渡期兼容。 */
export type ContainerBlock = never;

export interface BlockLocation {
  block: unknown;
  siblings: unknown[];
  index: number;
  parentBlock: unknown | null;
  parentId: string | null;
  parentType: string;
  sectionId: string | null;
  sectionTitle: string | null;
}

export function getBlockIndent(_block: unknown): number {
  return 0;
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
  return {
    ...content,
    [section]: value,
  };
}

export function setLessonPlanSectionStatus(
  content: LessonPlanContent,
  section: LessonPlanSectionName,
  status: SectionStatus,
): LessonPlanContent {
  return {
    ...content,
    [`${section}_status`]: status,
  };
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

export function setStudyGuideSectionStatus(
  content: StudyGuideContent,
  section: StudyGuideSectionName,
  status: SectionStatus,
): StudyGuideContent {
  return {
    ...content,
    [`${section}_status`]: status,
  };
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

// ---------------------------------------------------------------------------
// Section 提取（将结构化内容模型转为 SectionBlock[]）
// ---------------------------------------------------------------------------

let _blockIdCounter = 0;

function nextBlockId(): string {
  _blockIdCounter++;
  return `blk-${_blockIdCounter}`;
}

function makeParagraphBlock(text: string, status: SectionStatus = 'confirmed'): Block {
  return {
    id: nextBlockId(),
    type: 'paragraph',
    status,
    source: 'ai',
    content: text,
  };
}

function makeListBlock(items: string[], status: SectionStatus = 'confirmed'): Block {
  return {
    id: nextBlockId(),
    type: 'list',
    status,
    source: 'ai',
    items,
  };
}

function makeTeachingStepBlock(
  step: TeachingProcessStep,
  status: SectionStatus = 'confirmed',
): Block {
  const children: Block[] = [];
  if (step.teacher_activity) {
    children.push(makeParagraphBlock(`教师：${step.teacher_activity}`, status));
  }
  if (step.student_activity) {
    children.push(makeParagraphBlock(`学生：${step.student_activity}`, status));
  }
  if (step.design_intent) {
    children.push(makeParagraphBlock(`设计意图：${step.design_intent}`, status));
  }
  return {
    id: nextBlockId(),
    type: 'teaching_step',
    status,
    source: 'ai',
    title: step.phase,
    durationMinutes: step.duration,
    children,
  };
}

function collectLessonPlanSections(content: LessonPlanContent): SectionBlock[] {
  const sections: SectionBlock[] = [];

  // 教学目标
  sections.push({
    id: 'section-objectives',
    type: 'section',
    title: '教学目标',
    status: content.objectives_status,
    source: 'ai',
    children: content.objectives.map((obj) =>
      makeParagraphBlock(`【${obj.dimension === 'knowledge' ? '知识与技能' : obj.dimension === 'ability' ? '过程与方法' : '情感态度与价值观'}】${obj.content}`, content.objectives_status),
    ),
  });

  // 教学重难点
  const kpChildren: Block[] = [];
  if (content.key_points.keyPoints.length > 0) {
    kpChildren.push(makeListBlock(content.key_points.keyPoints.map((p) => `重点：${p}`), content.key_points_status));
  }
  if (content.key_points.difficulties.length > 0) {
    kpChildren.push(makeListBlock(content.key_points.difficulties.map((d) => `难点：${d}`), content.key_points_status));
  }
  sections.push({
    id: 'section-key_points',
    type: 'section',
    title: '教学重难点',
    status: content.key_points_status,
    source: 'ai',
    children: kpChildren,
  });

  // 教学准备
  sections.push({
    id: 'section-preparation',
    type: 'section',
    title: '教学准备',
    status: content.preparation_status,
    source: 'ai',
    children: content.preparation.length > 0
      ? [makeListBlock(content.preparation, content.preparation_status)]
      : [],
  });

  // 教学过程
  sections.push({
    id: 'section-teaching_process',
    type: 'section',
    title: '教学过程',
    status: content.teaching_process_status,
    source: 'ai',
    children: content.teaching_process.map((step) =>
      makeTeachingStepBlock(step, content.teaching_process_status),
    ),
  });

  // 板书设计
  sections.push({
    id: 'section-board_design',
    type: 'section',
    title: '板书设计',
    status: content.board_design_status,
    source: 'ai',
    children: content.board_design
      ? [makeParagraphBlock(content.board_design, content.board_design_status)]
      : [],
  });

  // 教学反思
  sections.push({
    id: 'section-reflection',
    type: 'section',
    title: '教学反思',
    status: content.reflection_status,
    source: 'ai',
    children: content.reflection
      ? [makeParagraphBlock(content.reflection, content.reflection_status)]
      : [],
  });

  return sections;
}

function collectStudyGuideSections(content: StudyGuideContent): SectionBlock[] {
  const sections: SectionBlock[] = [];

  // 学习目标
  sections.push({
    id: 'section-learning_objectives',
    type: 'section',
    title: '学习目标',
    status: content.learning_objectives_status,
    source: 'ai',
    children: content.learning_objectives.length > 0
      ? [makeListBlock(content.learning_objectives, content.learning_objectives_status)]
      : [],
  });

  // 重点难点预测
  sections.push({
    id: 'section-key_difficulties',
    type: 'section',
    title: '重点难点预测',
    status: content.key_difficulties_status,
    source: 'ai',
    children: content.key_difficulties.length > 0
      ? [makeListBlock(content.key_difficulties, content.key_difficulties_status)]
      : [],
  });

  // 知识链接
  sections.push({
    id: 'section-prior_knowledge',
    type: 'section',
    title: '知识链接',
    status: content.prior_knowledge_status,
    source: 'ai',
    children: content.prior_knowledge.length > 0
      ? [makeListBlock(content.prior_knowledge, content.prior_knowledge_status)]
      : [],
  });

  // 自主学习
  sections.push({
    id: 'section-self_study',
    type: 'section',
    title: '自主学习',
    status: content.self_study_status,
    source: 'ai',
    children: content.learning_process.selfStudy.map((item) =>
      makeParagraphBlock(`[${item.level}级] ${item.prompt}`, content.self_study_status),
    ),
  });

  // 合作探究
  sections.push({
    id: 'section-collaboration',
    type: 'section',
    title: '合作探究',
    status: content.collaboration_status,
    source: 'ai',
    children: content.learning_process.collaboration.map((item) =>
      makeParagraphBlock(`[${item.level}级] ${item.prompt}`, content.collaboration_status),
    ),
  });

  // 展示提升
  sections.push({
    id: 'section-presentation',
    type: 'section',
    title: '展示提升',
    status: content.presentation_status,
    source: 'ai',
    children: content.learning_process.presentation.map((item) =>
      makeParagraphBlock(`[${item.level}级] ${item.prompt}`, content.presentation_status),
    ),
  });

  // 达标测评
  sections.push({
    id: 'section-assessment',
    type: 'section',
    title: '达标测评',
    status: content.assessment_status,
    source: 'ai',
    children: content.assessment.map((item) =>
      makeParagraphBlock(`[${item.level}级] ${item.prompt}`, content.assessment_status),
    ),
  });

  // 拓展延伸
  sections.push({
    id: 'section-extension',
    type: 'section',
    title: '拓展延伸',
    status: content.extension_status,
    source: 'ai',
    children: content.extension.map((item) =>
      makeParagraphBlock(`[${item.level}级] ${item.prompt}`, content.extension_status),
    ),
  });

  // 自主反思
  sections.push({
    id: 'section-self_reflection',
    type: 'section',
    title: '自主反思',
    status: content.self_reflection_status,
    source: 'ai',
    children: content.self_reflection
      ? [makeParagraphBlock(content.self_reflection, content.self_reflection_status)]
      : [],
  });

  return sections;
}

// ---------------------------------------------------------------------------
// 旧 block 系统兼容 stub（Sprint 4 编辑器重写后移除）
// ---------------------------------------------------------------------------

export function cloneContent(content: ContentDocument): ContentDocument {
  return cloneSerializable(content);
}

export function collectSections(content: ContentDocument): SectionBlock[] {
  if (isLessonPlan(content)) {
    return collectLessonPlanSections(content);
  }
  if (isStudyGuide(content)) {
    return collectStudyGuideSections(content);
  }
  return [];
}

export function findSection(content: ContentDocument, sectionId: string): SectionBlock | undefined {
  return collectSections(content).find((s) => s.id === sectionId);
}

export function findBlockLocation(
  _content: ContentDocument,
  _targetBlockId: string,
): BlockLocation | null {
  return null;
}

export function canInsertChild(_parentType: string, _childType: string): boolean {
  return false;
}

export function createBlock<T extends BlockType>(_type: T): unknown {
  return null;
}

export function acceptPendingBlock(_content: ContentDocument, _blockId: string): ContentDocument {
  return _content;
}

export function rejectPendingBlock(_content: ContentDocument, _blockId: string): ContentDocument {
  return _content;
}

export function appendBlockToContainer(
  _content: ContentDocument,
  _parentId: string,
  _type: string,
): ContentDocument {
  return _content;
}

export function appendExistingBlockToContainer(
  _content: ContentDocument,
  _sectionId: string,
  _block: unknown,
): ContentDocument {
  return _content;
}

export function insertExistingBlockAfter(
  _content: ContentDocument,
  _blockId: string,
  _newBlock: unknown,
): ContentDocument {
  return _content;
}

export function updateBlock(
  _content: ContentDocument,
  _blockId: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  _updater?: (block: any) => any,
): ContentDocument {
  return _content;
}

export function deleteBlock(_content: ContentDocument, _blockId: string): ContentDocument {
  return _content;
}

export function moveBlock(
  _content: ContentDocument,
  _blockId: string,
  _direction: 'up' | 'down',
): ContentDocument {
  return _content;
}

export function reorderBlockBefore(
  _content: ContentDocument,
  _draggedId: string,
  _targetId: string,
  _parentId: string,
): ContentDocument {
  return _content;
}

export function convertBlockType(
  _content: ContentDocument,
  _blockId: string,
  _targetType: BlockType,
): ContentDocument {
  return _content;
}

export function adjustBlockIndent(
  _content: ContentDocument,
  _blockId: string,
  _direction: 'in' | 'out',
): ContentDocument {
  return _content;
}

export function getConfirmedContent(content: ContentDocument): ContentDocument {
  return content;
}

export function getConfirmedChildren(_section: SectionBlock): Block[] {
  return [];
}

export function getPendingChildren(_section: SectionBlock): Block[] {
  return [];
}
