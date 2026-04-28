export interface SemesterCreate {
  name: string;
  start_date: string;
  end_date: string;
  grade: string;
  subject: string;
}

export interface SemesterRead {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  grade: string;
  subject: string;
  week_count: number;
  created_at: string;
  updated_at: string;
}

export interface LessonScheduleEntryRead {
  id: string;
  week_schedule_id: string;
  task_id: string;
  day_of_week: number;
  class_period: number | null;
  notes: string | null;
  task_title: string;
  task_subject: string;
  task_grade: string;
  created_at: string;
}

export interface WeekScheduleRead {
  id: string;
  semester_id: string;
  week_number: number;
  label: string;
  start_date: string;
  end_date: string;
  notes: string | null;
  entries: LessonScheduleEntryRead[];
}

export interface SemesterDetailRead extends SemesterRead {
  weeks: WeekScheduleRead[];
}

export interface LessonScheduleEntryCreate {
  task_id: string;
  day_of_week: number;
  class_period?: number | null;
  notes?: string | null;
}

export interface LessonScheduleEntryUpdate {
  day_of_week?: number | null;
  class_period?: number | null;
  notes?: string | null;
}

export interface SemesterUpdate {
  name?: string | null;
  start_date?: string | null;
  end_date?: string | null;
}
