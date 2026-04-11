export type BlockStatus = 'confirmed' | 'pending';

export type BlockSource = 'human' | 'ai';

export interface BlockBase {
  id: string;
  type: 'section' | 'paragraph' | 'list' | 'teaching_step';
  status: BlockStatus;
  source: BlockSource;
}

export interface ParagraphBlock extends BlockBase {
  type: 'paragraph';
  content: string;
}

export interface ListBlock extends BlockBase {
  type: 'list';
  items: string[];
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

export type Block = ParagraphBlock | ListBlock | SectionBlock | TeachingStepBlock;

export interface ContentDocument {
  version: number;
  blocks: Block[];
}

export const isContainerBlock = (
  block: Block,
): block is SectionBlock | TeachingStepBlock => block.type === 'section' || block.type === 'teaching_step';

export const isPendingBlock = (block: Block): boolean => block.status === 'pending';

