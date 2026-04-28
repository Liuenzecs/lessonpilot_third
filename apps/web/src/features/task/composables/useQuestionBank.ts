import { ref, watch } from 'vue';
import { request } from '@/shared/api/client';

export interface Question {
  id: string;
  chapter: string;
  grade: string;
  question_type: string;
  difficulty: string;
  prompt: string;
  options: string[] | null;
  answer: string;
  analysis: string;
  source: string;
  tags: string[] | null;
  subject: string;
}

export interface QuestionListResponse {
  items: Question[];
  total: number;
  limit: number;
  offset: number;
}

export function useQuestionBank() {
  const chapters = ref<string[]>([]);
  const questions = ref<Question[]>([]);
  const total = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const selectedChapter = ref<string | null>(null);
  const selectedDifficulty = ref<string | null>(null);
  const selectedType = ref<string | null>(null);

  async function fetchChapters() {
    try {
      const data = await request<{ chapter: string }[]>('/api/v1/questions/chapters');
      chapters.value = data.map((d: { chapter: string }) => d.chapter);
    } catch {
      chapters.value = [];
    }
  }

  async function fetchQuestions() {
    loading.value = true;
    error.value = null;
    try {
      const params = new URLSearchParams();
      if (selectedChapter.value) params.set('chapter', selectedChapter.value);
      if (selectedDifficulty.value) params.set('difficulty', selectedDifficulty.value);
      if (selectedType.value) params.set('question_type', selectedType.value);
      params.set('limit', '200');

      const data = await request<QuestionListResponse>(`/api/v1/questions/?${params.toString()}`);
      questions.value = data.items;
      total.value = data.total;
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : '加载题库失败';
      questions.value = [];
    } finally {
      loading.value = false;
    }
  }

  watch([selectedChapter, selectedDifficulty, selectedType], () => {
    void fetchQuestions();
  });

  const typeLabel: Record<string, string> = {
    choice: '选择题',
    fill_blank: '填空题',
    short_answer: '简答题',
  };

  const difficultyLabel: Record<string, string> = {
    A: 'A级（基础）',
    B: 'B级（理解）',
    C: 'C级（拓展）',
    D: 'D级（选做）',
  };

  const difficultyClass: Record<string, string> = {
    A: 'level-a',
    B: 'level-b',
    C: 'level-c',
    D: 'level-d',
  };

  return {
    chapters,
    questions,
    total,
    loading,
    error,
    selectedChapter,
    selectedDifficulty,
    selectedType,
    fetchChapters,
    fetchQuestions,
    typeLabel,
    difficultyLabel,
    difficultyClass,
  };
}
