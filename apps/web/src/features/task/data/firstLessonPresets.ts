import type { LessonCategory, LessonType, Scene } from '@lessonpilot/shared-types';

export const FIRST_LESSON_PRESET_QUERY = 'first-lesson';

export interface FirstLessonPreset {
  subject: string;
  grade: string;
  topic: string;
  class_hour: number;
  lesson_category: LessonCategory;
  lesson_type: LessonType;
  scene: Scene;
  requirements: string;
}

export const FIRST_LESSON_PRESET: FirstLessonPreset = {
  subject: '语文',
  grade: '七年级',
  topic: '朱自清《春》 第一课时',
  class_hour: 1,
  lesson_category: 'new',
  lesson_type: 'lesson_plan',
  scene: 'public_school',
  requirements:
    '用于新老师试用：生成一份可提交的公立校教案，重点品读春草图和春花图，教学过程不少于 4 个环节，保留板书设计和课后反思空白。',
};
