import { mount } from '@vue/test-utils';
import { defineComponent } from 'vue';
import { describe, expect, it } from 'vitest';

import SectionPanel from '../SectionPanel.vue';

const AssessmentEditorStub = defineComponent({
  name: 'AssessmentEditor',
  template: '<div data-testid="assessment-editor-stub" />',
});

const GenericListEditorStub = defineComponent({
  name: 'GenericListEditor',
  template: '<div data-testid="generic-list-editor-stub" />',
});

const RichTextEditorStub = defineComponent({
  name: 'RichTextEditor',
  template: '<div data-testid="rich-text-editor-stub" />',
});

const KeyPointsEditorStub = defineComponent({
  name: 'KeyPointsEditor',
  template: '<div data-testid="key-points-editor-stub" />',
});

const ObjectivesEditorStub = defineComponent({
  name: 'ObjectivesEditor',
  template: '<div data-testid="objectives-editor-stub" />',
});

const TeachingProcessEditorStub = defineComponent({
  name: 'TeachingProcessEditor',
  template: '<div data-testid="teaching-process-editor-stub" />',
});

const SectionAiActionsStub = defineComponent({
  name: 'SectionAiActions',
  template: '<div data-testid="section-ai-actions-stub" />',
});

const CitationTooltipStub = defineComponent({
  name: 'CitationTooltip',
  template: '<div data-testid="citation-tooltip-stub" />',
});

function mountSectionPanel(overrides: Record<string, unknown>) {
  return mount(SectionPanel, {
    props: {
      section: { name: 'self_study', title: '自主学习', status: 'pending' },
      docType: 'study_guide',
      sectionData: [],
      sectionReferences: [],
      collapsed: false,
      streamingText: '',
      isRewriting: false,
      ...overrides,
    },
    global: {
      stubs: {
        AssessmentEditor: AssessmentEditorStub,
        GenericListEditor: GenericListEditorStub,
        RichTextEditor: RichTextEditorStub,
        KeyPointsEditor: KeyPointsEditorStub,
        ObjectivesEditor: ObjectivesEditorStub,
        TeachingProcessEditor: TeachingProcessEditorStub,
        SectionAiActions: SectionAiActionsStub,
        CitationTooltip: CitationTooltipStub,
      },
    },
  });
}

describe('SectionPanel', () => {
  it('renders AssessmentEditor for study guide self_study section', () => {
    const wrapper = mountSectionPanel({});

    expect(wrapper.find('[data-testid="assessment-editor-stub"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="rich-text-editor-stub"]').exists()).toBe(false);
  });

  it('renders GenericListEditor for study guide learning objectives', () => {
    const wrapper = mountSectionPanel({
      section: { name: 'learning_objectives', title: '学习目标', status: 'pending' },
      sectionData: ['目标一'],
    });

    expect(wrapper.find('[data-testid="generic-list-editor-stub"]').exists()).toBe(true);
  });

  it('renders RichTextEditor for study guide self_reflection', () => {
    const wrapper = mountSectionPanel({
      section: { name: 'self_reflection', title: '自主反思', status: 'pending' },
      sectionData: '',
    });

    expect(wrapper.find('[data-testid="rich-text-editor-stub"]').exists()).toBe(true);
    expect(wrapper.find('[data-testid="assessment-editor-stub"]').exists()).toBe(false);
  });
});
