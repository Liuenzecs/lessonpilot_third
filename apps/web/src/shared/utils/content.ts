import type {
  Block,
  BlockSuggestion,
  BlockType,
  ChoiceQuestionBlock,
  ContentDocument,
  ExerciseGroupBlock,
  ExerciseQuestionBlock,
  FillBlankQuestionBlock,
  ListBlock,
  ParagraphBlock,
  SectionBlock,
  ShortAnswerQuestionBlock,
  TeachingStepBlock,
} from '@lessonpilot/shared-types';
import { isContainerBlock } from '@lessonpilot/shared-types';

export type ContainerBlock = SectionBlock | TeachingStepBlock | ExerciseGroupBlock;
export type InsertableBlockType = Exclude<BlockType, 'section'>;

export interface BlockLocation {
  block: Block;
  siblings: Block[];
  index: number;
  parentBlock: ContainerBlock | null;
  parentId: string | null;
  parentType: 'root' | ContainerBlock['type'];
  sectionId: string | null;
  sectionTitle: string | null;
}

export function cloneSerializable<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

export function cloneContent(content: ContentDocument): ContentDocument {
  return cloneSerializable(content);
}

export function collectSections(content: ContentDocument): SectionBlock[] {
  return content.blocks.filter((block): block is SectionBlock => block.type === 'section');
}

export function findSection(content: ContentDocument, sectionId: string): SectionBlock | undefined {
  return collectSections(content).find((section) => section.id === sectionId);
}

export function normalizeIndent(level: number | undefined | null): number {
  if (!Number.isFinite(level)) {
    return 0;
  }
  return Math.max(0, Math.min(6, Math.trunc(level ?? 0)));
}

export function getBlockIndent(block: Block): number {
  if (block.type === 'paragraph' || block.type === 'list') {
    return normalizeIndent(block.indent);
  }
  return 0;
}

function getChildren(block: Block): Block[] | null {
  if (!isContainerBlock(block)) {
    return null;
  }
  return block.children as Block[];
}

function toPlainText(value: string): string {
  return value.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function buildParagraphsFromLines(lines: string[]): string {
  const safeLines = lines.filter((line) => line.trim().length > 0);
  if (!safeLines.length) {
    return '<p></p>';
  }
  return safeLines.map((line) => `<p>${line.trim()}</p>`).join('');
}

function createSuggestionlessConfirmedBlock(block: Block, nextId?: string): Block {
  const nextBlock = cloneSerializable(block);
  clearSuggestionDeep(nextBlock);
  nextBlock.status = 'confirmed';
  if (nextId) {
    nextBlock.id = nextId;
  }
  return nextBlock;
}

function clearSuggestionDeep(block: Block): void {
  delete block.suggestion;
  block.status = 'confirmed';
  const children = getChildren(block);
  if (children) {
    children.forEach((child) => clearSuggestionDeep(child));
  }
}

function removeBlockById(blocks: Block[], blockId: string): Block[] {
  return blocks
    .filter((block) => block.id !== blockId)
    .map((block) => {
      const children = getChildren(block);
      if (!children) {
        return block;
      }
      return {
        ...block,
        children: removeBlockById(children, blockId),
      } as Block;
    });
}

function removeReplaceSuggestionsForTarget(blocks: Block[], targetBlockId: string, exceptBlockId?: string): Block[] {
  return blocks
    .filter((block) => {
      const suggestion = block.suggestion;
      return !(
        block.status === 'pending' &&
        suggestion?.kind === 'replace' &&
        suggestion.targetBlockId === targetBlockId &&
        block.id !== exceptBlockId
      );
    })
    .map((block) => {
      const children = getChildren(block);
      if (!children) {
        return block;
      }
      return {
        ...block,
        children: removeReplaceSuggestionsForTarget(children, targetBlockId, exceptBlockId),
      } as Block;
    });
}

export function findBlockLocation(content: ContentDocument, blockId: string): BlockLocation | null {
  return findBlockLocationByPredicate(content, (block) => block.id === blockId);
}

function findBlockLocationByPredicate(
  content: ContentDocument,
  predicate: (block: Block) => boolean,
): BlockLocation | null {
  const walk = (
    siblings: Block[],
    parentBlock: ContainerBlock | null,
    section: SectionBlock | null,
  ): BlockLocation | null => {
    for (const [index, block] of siblings.entries()) {
      const currentSection = block.type === 'section' ? block : section;
      if (predicate(block)) {
        return {
          block,
          siblings,
          index,
          parentBlock,
          parentId: parentBlock?.id ?? null,
          parentType: parentBlock?.type ?? 'root',
          sectionId: currentSection?.id ?? null,
          sectionTitle: currentSection?.title ?? null,
        };
      }

      const children = getChildren(block);
      if (!children) {
        continue;
      }

      const found = walk(children, block as ContainerBlock, currentSection);
      if (found) {
        return found;
      }
    }

    return null;
  };

  return walk(content.blocks, null, null);
}

function findPendingBlockLocation(content: ContentDocument, blockId: string): BlockLocation | null {
  return findBlockLocationByPredicate(
    content,
    (block) => block.id === blockId && block.status === 'pending',
  );
}

export function createBlock<T extends InsertableBlockType>(type: T): Extract<Block, { type: T }> {
  const base = {
    id: crypto.randomUUID(),
    status: 'confirmed' as const,
    source: 'human' as const,
  };

  switch (type) {
    case 'paragraph':
      return {
        ...base,
        type,
        content: '<p></p>',
        indent: 0,
      } satisfies ParagraphBlock as Extract<Block, { type: T }>;
    case 'list':
      return {
        ...base,
        type,
        items: [''],
        indent: 0,
      } satisfies ListBlock as Extract<Block, { type: T }>;
    case 'teaching_step':
      return {
        ...base,
        type,
        title: '新教学步骤',
        durationMinutes: null,
        children: [],
      } satisfies TeachingStepBlock as Extract<Block, { type: T }>;
    case 'exercise_group':
      return {
        ...base,
        type,
        title: '新题组',
        children: [],
      } satisfies ExerciseGroupBlock as Extract<Block, { type: T }>;
    case 'choice_question':
      return {
        ...base,
        type,
        prompt: '<p></p>',
        options: ['选项 A', '选项 B', '选项 C', '选项 D'],
        answers: [],
        analysis: '<p></p>',
      } satisfies ChoiceQuestionBlock as Extract<Block, { type: T }>;
    case 'fill_blank_question':
      return {
        ...base,
        type,
        prompt: '<p></p>',
        answers: [''],
        analysis: '<p></p>',
      } satisfies FillBlankQuestionBlock as Extract<Block, { type: T }>;
    case 'short_answer_question':
      return {
        ...base,
        type,
        prompt: '<p></p>',
        referenceAnswer: '<p></p>',
        analysis: '<p></p>',
      } satisfies ShortAnswerQuestionBlock as Extract<Block, { type: T }>;
    default:
      throw new Error(`Unsupported block type: ${String(type)}`);
  }
}

export function canInsertChild(parentType: BlockType | 'root', childType: InsertableBlockType): boolean {
  if (parentType === 'section') {
    return ['paragraph', 'list', 'teaching_step', 'exercise_group'].includes(childType);
  }
  if (parentType === 'teaching_step') {
    return ['paragraph', 'list'].includes(childType);
  }
  if (parentType === 'exercise_group') {
    return ['choice_question', 'fill_blank_question', 'short_answer_question'].includes(childType);
  }
  return false;
}

export function appendBlockToContainer(
  content: ContentDocument,
  parentId: string,
  childType: InsertableBlockType,
): ContentDocument {
  return appendExistingBlockToContainer(content, parentId, createBlock(childType));
}

export function appendExistingBlockToContainer(
  content: ContentDocument,
  parentId: string,
  block: Block,
): ContentDocument {
  const nextContent = cloneContent(content);
  const location = findBlockLocation(nextContent, parentId);
  if (
    !location ||
    block.type === 'section' ||
    !canInsertChild(location.block.type, block.type) ||
    !isContainerBlock(location.block)
  ) {
    return nextContent;
  }

  (location.block.children as Block[]).push(block);
  return nextContent;
}

export function insertBlockAfter(
  content: ContentDocument,
  blockId: string,
  childType: InsertableBlockType,
): ContentDocument {
  return insertExistingBlockAfter(content, blockId, createBlock(childType));
}

export function insertExistingBlockAfter(
  content: ContentDocument,
  blockId: string,
  block: Block,
): ContentDocument {
  const nextContent = cloneContent(content);
  const location = findBlockLocation(nextContent, blockId);
  if (!location || block.type === 'section' || !canInsertChild(location.parentType, block.type)) {
    return nextContent;
  }

  location.siblings.splice(location.index + 1, 0, block);
  return nextContent;
}

export function updateBlock(
  content: ContentDocument,
  blockId: string,
  updater: (block: Block) => Block,
): ContentDocument {
  const nextContent = cloneContent(content);
  const location = findBlockLocation(nextContent, blockId);
  if (!location) {
    return nextContent;
  }

  location.siblings.splice(location.index, 1, updater(location.block));
  return nextContent;
}

export function moveBlock(
  content: ContentDocument,
  blockId: string,
  direction: 'up' | 'down',
): ContentDocument {
  const nextContent = cloneContent(content);
  const location = findBlockLocation(nextContent, blockId);
  if (!location) {
    return nextContent;
  }

  const targetIndex = direction === 'up' ? location.index - 1 : location.index + 1;
  if (targetIndex < 0 || targetIndex >= location.siblings.length) {
    return nextContent;
  }

  const [block] = location.siblings.splice(location.index, 1);
  location.siblings.splice(targetIndex, 0, block);
  return nextContent;
}

export function adjustBlockIndent(
  content: ContentDocument,
  blockId: string,
  direction: 'in' | 'out',
): ContentDocument {
  return updateBlock(content, blockId, (block) => {
    if (block.type !== 'paragraph' && block.type !== 'list') {
      return block;
    }

    return {
      ...block,
      indent: normalizeIndent(getBlockIndent(block) + (direction === 'in' ? 1 : -1)),
    };
  });
}

export function reorderBlockBefore(
  content: ContentDocument,
  draggedId: string,
  targetId: string,
  parentId: string,
): ContentDocument {
  const nextContent = cloneContent(content);
  const dragged = findBlockLocation(nextContent, draggedId);
  const target = findBlockLocation(nextContent, targetId);
  if (!dragged || !target || dragged.parentId !== parentId || target.parentId !== parentId) {
    return nextContent;
  }

  const [draggedBlock] = dragged.siblings.splice(dragged.index, 1);
  const refreshedTarget = findBlockLocation(nextContent, targetId);
  if (!refreshedTarget) {
    return nextContent;
  }
  refreshedTarget.siblings.splice(refreshedTarget.index, 0, draggedBlock);
  return nextContent;
}

export function deleteBlock(content: ContentDocument, blockId: string): ContentDocument {
  const nextContent = cloneContent(content);
  nextContent.blocks = removeBlockById(nextContent.blocks, blockId);
  return nextContent;
}

function ensureChoiceOptions(options: string[], answers: string[]): string[] {
  const merged = [...options.filter(Boolean), ...answers.filter(Boolean)];
  while (merged.length < 4) {
    merged.push(`选项 ${String.fromCharCode(65 + merged.length)}`);
  }
  return merged.slice(0, 4);
}

function convertToQuestionBlock(block: ExerciseQuestionBlock, targetType: BlockType): ExerciseQuestionBlock {
  const prompt = block.prompt;
  const analysis = block.analysis;

  if (targetType === 'choice_question') {
    const options =
      block.type === 'choice_question'
        ? ensureChoiceOptions(block.options, block.answers)
        : block.type === 'fill_blank_question'
          ? ensureChoiceOptions([], block.answers)
          : ensureChoiceOptions([], [toPlainText(block.referenceAnswer)]);
    const answers =
      block.type === 'short_answer_question'
        ? [toPlainText(block.referenceAnswer)].filter(Boolean)
        : [...block.answers];

    return {
      id: block.id,
      type: 'choice_question',
      status: block.status,
      source: block.source,
      suggestion: block.suggestion,
      prompt,
      options,
      answers,
      analysis,
    };
  }

  if (targetType === 'fill_blank_question') {
    const answers =
      block.type === 'short_answer_question'
        ? [toPlainText(block.referenceAnswer)].filter(Boolean)
        : [...block.answers];

    return {
      id: block.id,
      type: 'fill_blank_question',
      status: block.status,
      source: block.source,
      suggestion: block.suggestion,
      prompt,
      answers: answers.length ? answers : [''],
      analysis,
    };
  }

  const referenceAnswer =
    block.type === 'short_answer_question'
      ? block.referenceAnswer
      : buildParagraphsFromLines(block.answers.length ? block.answers : ['']);

  return {
    id: block.id,
    type: 'short_answer_question',
    status: block.status,
    source: block.source,
    suggestion: block.suggestion,
    prompt,
    referenceAnswer,
    analysis,
  };
}

export function convertBlockType(
  content: ContentDocument,
  blockId: string,
  targetType: BlockType,
): ContentDocument {
  return updateBlock(content, blockId, (block) => {
    if (block.type === targetType) {
      return block;
    }

    if (block.type === 'paragraph' && targetType === 'list') {
      const items = toPlainText(block.content).split(/\n|。|；|;|\./).map((item) => item.trim()).filter(Boolean);
      return {
        id: block.id,
        type: 'list',
        status: block.status,
        source: block.source,
        suggestion: block.suggestion,
        indent: getBlockIndent(block),
        items: items.length ? items : [''],
      } satisfies ListBlock;
    }

    if (block.type === 'list' && targetType === 'paragraph') {
      return {
        id: block.id,
        type: 'paragraph',
        status: block.status,
        source: block.source,
        suggestion: block.suggestion,
        content: buildParagraphsFromLines(block.items),
        indent: getBlockIndent(block),
      } satisfies ParagraphBlock;
    }

    if (
      ['choice_question', 'fill_blank_question', 'short_answer_question'].includes(block.type) &&
      ['choice_question', 'fill_blank_question', 'short_answer_question'].includes(targetType)
    ) {
      return convertToQuestionBlock(block as ExerciseQuestionBlock, targetType);
    }

    return block;
  });
}

export function acceptPendingBlock(content: ContentDocument, blockId: string): ContentDocument {
  const nextContent = cloneContent(content);
  const location = findPendingBlockLocation(nextContent, blockId);
  if (!location || location.block.status !== 'pending') {
    return nextContent;
  }

  const suggestion = location.block.suggestion as BlockSuggestion | undefined;
  if (suggestion?.kind === 'replace' && suggestion.targetBlockId) {
    const replacement = createSuggestionlessConfirmedBlock(location.block, suggestion.targetBlockId);
    nextContent.blocks = removeReplaceSuggestionsForTarget(nextContent.blocks, suggestion.targetBlockId, blockId);
    const refreshedPendingLocation = findPendingBlockLocation(nextContent, blockId);
    const targetLocation = findBlockLocation(nextContent, suggestion.targetBlockId);
    if (refreshedPendingLocation && targetLocation) {
      targetLocation.siblings.splice(targetLocation.index, 1, replacement);
      refreshedPendingLocation.siblings.splice(refreshedPendingLocation.index, 1);
      return nextContent;
    }
  }

  clearSuggestionDeep(location.block);
  return nextContent;
}

export function rejectPendingBlock(content: ContentDocument, blockId: string): ContentDocument {
  const nextContent = cloneContent(content);
  nextContent.blocks = removeBlockById(nextContent.blocks, blockId);
  return nextContent;
}

export function getConfirmedChildren(section: SectionBlock): Block[] {
  return section.children.filter((child) => child.status === 'confirmed');
}

export function getPendingChildren(section: SectionBlock): Block[] {
  return section.children.filter((child) => child.status === 'pending');
}

function collectConfirmedBlocks(blocks: Block[]): Block[] {
  const confirmedBlocks: Block[] = [];

  blocks.forEach((block) => {
    if (block.status !== 'confirmed') {
      return;
    }

    if (!isContainerBlock(block)) {
      confirmedBlocks.push(cloneSerializable(block));
      return;
    }

    confirmedBlocks.push({
      ...cloneSerializable(block),
      children: collectConfirmedBlocks(block.children as Block[]) as typeof block.children,
    } as Block);
  });

  return confirmedBlocks;
}

export function getConfirmedContent(content: ContentDocument): ContentDocument {
  return {
    version: content.version,
    blocks: collectConfirmedBlocks(content.blocks),
  };
}
