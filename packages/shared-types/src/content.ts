export type BlockStatus = 'confirmed' | 'pending';

export type BlockSource = 'human' | 'ai';

export type SuggestionKind = 'append' | 'replace';

export type SuggestionAction = 'rewrite' | 'polish' | 'expand';

export type SuggestionMode = 'block' | 'selection';

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
  kind: SuggestionKind;
  targetBlockId?: string;
  action?: SuggestionAction;
  mode?: SuggestionMode;
  selectionText?: string;
}

export interface BlockBase {
  id: string;
  type: BlockType;
  status: BlockStatus;
  source: BlockSource;
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

export type TeachingStepChildBlock = ParagraphBlock | ListBlock;

export interface SectionBlock extends BlockBase {
  type: 'section';
  title: string;
  children: SectionChildBlock[];
}

export interface TeachingStepBlock extends BlockBase {
  type: 'teaching_step';
  title: string;
  durationMinutes: number | null;
  children: TeachingStepChildBlock[];
}

export type ExerciseQuestionBlock =
  | ChoiceQuestionBlock
  | FillBlankQuestionBlock
  | ShortAnswerQuestionBlock;

export interface ExerciseGroupBlock extends BlockBase {
  type: 'exercise_group';
  title: string;
  children: ExerciseQuestionBlock[];
}

export type SectionChildBlock =
  | ParagraphBlock
  | ListBlock
  | TeachingStepBlock
  | ExerciseGroupBlock;

export type Block =
  | SectionBlock
  | ParagraphBlock
  | ListBlock
  | TeachingStepBlock
  | ExerciseGroupBlock
  | ChoiceQuestionBlock
  | FillBlankQuestionBlock
  | ShortAnswerQuestionBlock;

export interface ContentDocument {
  version: number;
  blocks: Block[];
}

export const isContainerBlock = (
  block: Block,
): block is SectionBlock | TeachingStepBlock | ExerciseGroupBlock =>
  block.type === 'section' || block.type === 'teaching_step' || block.type === 'exercise_group';

export const isQuestionBlock = (block: Block): block is ExerciseQuestionBlock =>
  block.type === 'choice_question' ||
  block.type === 'fill_blank_question' ||
  block.type === 'short_answer_question';

export const isPendingBlock = (block: Block): boolean => block.status === 'pending';
