import type {
  Block,
  ContentDocument,
  ListBlock,
  ParagraphBlock,
  SectionBlock,
  TeachingStepBlock,
} from '@lessonpilot/shared-types';

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

export function addParagraphBlock(section: SectionBlock): void {
  section.children.push({
    id: crypto.randomUUID(),
    type: 'paragraph',
    content: '<p></p>',
    status: 'confirmed',
    source: 'human',
  } satisfies ParagraphBlock);
}

export function addListBlock(section: SectionBlock): void {
  section.children.push({
    id: crypto.randomUUID(),
    type: 'list',
    items: [''],
    status: 'confirmed',
    source: 'human',
  } satisfies ListBlock);
}

function walkChildren(blocks: Block[], callback: (block: Block, index: number, siblings: Block[]) => void): void {
  blocks.forEach((block, index) => {
    callback(block, index, blocks);
    if (block.type === 'section' || block.type === 'teaching_step') {
      walkChildren(block.children, callback);
    }
  });
}

export function acceptPendingBlock(content: ContentDocument, blockId: string): ContentDocument {
  const nextContent = cloneContent(content);
  walkChildren(nextContent.blocks, (block) => {
    if (block.id === blockId) {
      block.status = 'confirmed';
      if (block.type === 'section' || block.type === 'teaching_step') {
        walkChildren(block.children, (child) => {
          child.status = 'confirmed';
        });
      }
    }
  });
  return nextContent;
}

export function rejectPendingBlock(content: ContentDocument, blockId: string): ContentDocument {
  const nextContent = cloneContent(content);

  const removeFromChildren = (blocks: Block[]): Block[] =>
    blocks
      .filter((block) => block.id !== blockId)
      .map((block) => {
        if (block.type === 'section' || block.type === 'teaching_step') {
          return { ...block, children: removeFromChildren(block.children) };
        }
        return block;
      });

  return {
    ...nextContent,
    blocks: removeFromChildren(nextContent.blocks),
  };
}

export function updateBlockContent(
  content: ContentDocument,
  blockId: string,
  updater: (block: ParagraphBlock | ListBlock | TeachingStepBlock) => void,
): ContentDocument {
  const nextContent = cloneContent(content);
  walkChildren(nextContent.blocks, (block) => {
    if (block.id === blockId && block.type !== 'section') {
      updater(block as ParagraphBlock | ListBlock | TeachingStepBlock);
    }
  });
  return nextContent;
}

export function getConfirmedChildren(section: SectionBlock): Block[] {
  return section.children.filter((child) => child.status === 'confirmed');
}

export function getPendingChildren(section: SectionBlock): Block[] {
  return section.children.filter((child) => child.status === 'pending');
}
