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
// Section 元信息
// ---------------------------------------------------------------------------

export interface SectionInfo {
  name: string;
  title: string;
  status: SectionStatus;
}
