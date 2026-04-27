import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import TeachingPackagePanel from '../TeachingPackagePanel.vue';

describe('TeachingPackagePanel', () => {
  it('shows the package summary and emits generate', async () => {
    const wrapper = mount(TeachingPackagePanel, {
      props: {
        visible: true,
        loading: false,
        packageResult: {
          id: 'pkg-1',
          task_id: 'task-1',
          document_id: 'doc-1',
          title: '春上课包',
          status: 'pending',
          created_at: '2026-04-27',
          updated_at: '2026-04-27',
          content: {
            study_guide: {
              doc_type: 'study_guide',
              header: { title: '春学案', subject: '语文', grade: '七年级', className: '', studentName: '', date: '' },
              learning_objectives: ['我能朗读课文'],
              learning_objectives_status: 'pending',
              key_difficulties: [],
              key_difficulties_status: 'pending',
              prior_knowledge: [],
              prior_knowledge_status: 'pending',
              learning_process: { selfStudy: [], collaboration: [], presentation: [] },
              self_study_status: 'pending',
              collaboration_status: 'pending',
              presentation_status: 'pending',
              assessment: [],
              assessment_status: 'pending',
              extension: [],
              extension_status: 'pending',
              self_reflection: '',
              self_reflection_status: 'pending',
              section_references: {},
            },
            ppt_outline: [{ title: '导入', bullets: ['图片'], activity: '', speaker_note: '', status: 'pending' }],
            talk_script: { opening: '同学们', questions: ['你看到了什么？'], transitions: [], closing: '小结', status: 'pending' },
          },
        },
      },
    });

    expect(wrapper.text()).toContain('学案草稿');
    expect(wrapper.text()).toContain('PPT 大纲');
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('generate')).toHaveLength(1);
  });
});
