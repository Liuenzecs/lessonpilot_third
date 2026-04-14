export const SUBJECT_OPTIONS = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理'];

export const GRADE_OPTIONS = [
  '一年级',
  '二年级',
  '三年级',
  '四年级',
  '五年级',
  '六年级',
  '七年级',
  '八年级',
  '九年级',
  '高一',
  '高二',
  '高三',
];

export const LESSON_CATEGORY_OPTIONS = [
  { value: 'new', label: '新授课' },
  { value: 'review', label: '复习课' },
  { value: 'exercise', label: '练习课' },
  { value: 'comprehensive', label: '综合课' },
] as const;

export const SCENE_OPTIONS = [
  { value: 'public_school', label: '公立校' },
  { value: 'tutor', label: '家教' },
  { value: 'institution', label: '培训机构' },
] as const;

export const LESSON_TYPE_OPTIONS = [
  { value: 'lesson_plan', label: '教案' },
  { value: 'study_guide', label: '学案' },
  { value: 'both', label: '教案 + 学案' },
] as const;
