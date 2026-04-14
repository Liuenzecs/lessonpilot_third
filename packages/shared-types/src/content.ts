/**
 * 教案 / 学案结构化内容类型定义。
 *
 * 与后端 schemas/content.py 对齐。
 */

// ---------------------------------------------------------------------------
// 公共枚举
// ---------------------------------------------------------------------------

export type SectionStatus = 'confirmed' | 'pending';

export type Scene = 'public_school' | 'tutor' | 'institution';

export type LessonType = 'lesson_plan' | 'study_guide' | 'both';

export type LessonCategory = 'new' | 'review' | 'exercise' | 'comprehensive';

// ---------------------------------------------------------------------------
// 公共类型
// ---------------------------------------------------------------------------

export interface TeachingObjective {
  dimension: 'knowledge' | 'ability' | 'emotion';
  content: string;
}

export interface KeyPoints {
  keyPoints: string[];
  difficulties: string[];
}

export interface TeachingProcessStep {
  phase: string;
  duration: number;
  teacher_activity: string;
  student_activity: string;
  design_intent: string;
  status?: SectionStatus;
}

export interface AssessmentItem {
  level: 'A' | 'B' | 'C' | 'D';
  itemType: 'choice' | 'fill_blank' | 'short_answer';
  prompt: string;
  options: string[];
  answer: string;
  analysis: string;
}

// ---------------------------------------------------------------------------
// 教案
// ---------------------------------------------------------------------------

export interface LessonPlanHeader {
  title: string;
  subject: string;
  grade: string;
  classHour: number;
  lessonCategory: LessonCategory;
  teacher: string;
}

export interface LessonPlanContent {
  doc_type: 'lesson_plan';
  header: LessonPlanHeader;
  objectives: TeachingObjective[];
  objectives_status: SectionStatus;
  key_points: KeyPoints;
  key_points_status: SectionStatus;
  preparation: string[];
  preparation_status: SectionStatus;
  teaching_process: TeachingProcessStep[];
  teaching_process_status: SectionStatus;
  board_design: string;
  board_design_status: SectionStatus;
  reflection: string;
  reflection_status: SectionStatus;
}

// ---------------------------------------------------------------------------
// 学案
// ---------------------------------------------------------------------------

export interface StudyGuideHeader {
  title: string;
  subject: string;
  grade: string;
  className: string;
  studentName: string;
  date: string;
}

export interface LearningProcess {
  selfStudy: AssessmentItem[];
  collaboration: AssessmentItem[];
  presentation: AssessmentItem[];
}

export interface StudyGuideContent {
  doc_type: 'study_guide';
  header: StudyGuideHeader;
  learning_objectives: string[];
  learning_objectives_status: SectionStatus;
  key_difficulties: string[];
  key_difficulties_status: SectionStatus;
  prior_knowledge: string[];
  prior_knowledge_status: SectionStatus;
  learning_process: LearningProcess;
  self_study_status: SectionStatus;
  collaboration_status: SectionStatus;
  presentation_status: SectionStatus;
  assessment: AssessmentItem[];
  assessment_status: SectionStatus;
  extension: AssessmentItem[];
  extension_status: SectionStatus;
  self_reflection: string;
  self_reflection_status: SectionStatus;
}

// ---------------------------------------------------------------------------
// 联合类型 & 类型守卫
// ---------------------------------------------------------------------------

export type DocumentContent = LessonPlanContent | StudyGuideContent;

export function isLessonPlan(content: DocumentContent): content is LessonPlanContent {
  return content.doc_type === 'lesson_plan';
}

export function isStudyGuide(content: DocumentContent): content is StudyGuideContent {
  return content.doc_type === 'study_guide';
}

// ---------------------------------------------------------------------------
// 兼容旧 ContentDocument（过渡期使用，Sprint 4 编辑器重写后移除）
// ---------------------------------------------------------------------------

/** 旧 ContentDocument 类型别名 — 过渡期兼容。 */
export type ContentDocument = DocumentContent;

// ---------------------------------------------------------------------------
// 旧 block 类型兼容导出（Sprint 4 编辑器重写后移除）
// ---------------------------------------------------------------------------

export type BlockType =
  | 'section'
  | 'paragraph'
  | 'list'
  | 'teaching_step'
  | 'exercise_group'
  | 'choice_question'
  | 'fill_blank_question'
  | 'short_answer_question';

export interface BlockSuggestion {
  kind: 'append' | 'replace';
  targetBlockId?: string;
  action?: 'rewrite' | 'polish' | 'expand';
  mode?: 'block' | 'selection';
  selectionText?: string;
}

export interface BlockBase {
  id: string;
  type: BlockType;
  status: SectionStatus;
  source: 'human' | 'ai';
  suggestion?: BlockSuggestion;
}

export interface ParagraphBlock extends BlockBase {
  type: 'paragraph';
  content: string;
  indent?: number;
}

export interface ListBlock extends BlockBase {
  type: 'list';
  items: string[];
  indent?: number;
}

export interface ChoiceQuestionBlock extends BlockBase {
  type: 'choice_question';
  prompt: string;
  options: string[];
  answers: string[];
  analysis: string;
}

export interface FillBlankQuestionBlock extends BlockBase {
  type: 'fill_blank_question';
  prompt: string;
  answers: string[];
  analysis: string;
}

export interface ShortAnswerQuestionBlock extends BlockBase {
  type: 'short_answer_question';
  prompt: string;
  referenceAnswer: string;
  analysis: string;
}

export interface SectionBlock extends BlockBase {
  type: 'section';
  title: string;
  children: Block[];
}

export interface TeachingStepBlock extends BlockBase {
  type: 'teaching_step';
  title: string;
  durationMinutes: number | null;
  children: Block[];
}

export interface ExerciseGroupBlock extends BlockBase {
  type: 'exercise_group';
  title: string;
  children: Block[];
}

export type Block =
  | SectionBlock
  | ParagraphBlock
  | ListBlock
  | TeachingStepBlock
  | ExerciseGroupBlock
  | ChoiceQuestionBlock
  | FillBlankQuestionBlock
  | ShortAnswerQuestionBlock;

export const isContainerBlock = (block: Block): boolean =>
  block.type === 'section' || block.type === 'teaching_step' || block.type === 'exercise_group';

export const isPendingBlock = (block: Block): boolean => block.status === 'pending';
