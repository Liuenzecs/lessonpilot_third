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
// 旧 block 系统兼容 stub（Sprint 4 编辑器重写后移除）
// ---------------------------------------------------------------------------

export function cloneContent(content: ContentDocument): ContentDocument {
  return cloneSerializable(content);
}

export function collectSections(_content: ContentDocument): SectionBlock[] {
  return [];
}

export function findSection(_content: ContentDocument, _sectionId: string): SectionBlock | undefined {
  return undefined;
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
