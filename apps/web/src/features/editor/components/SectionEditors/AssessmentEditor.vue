<script setup lang="ts">
/**
 * 达标测评编辑器（学案）。
 * 编辑 AssessmentItem 数组，含题目类型、分级。
 */
import type { AssessmentItem } from '@lessonpilot/shared-types';
import { computed } from 'vue';

import FormulaText from '@/shared/components/FormulaText.vue';
import { containsFormula } from '@/shared/utils/formula';

const props = defineProps<{
  modelValue: AssessmentItem[];
  disabled?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: AssessmentItem[]];
}>();

const items = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

function updateItem(index: number, patch: Partial<AssessmentItem>) {
  const next = items.value.map((item, i) =>
    i === index ? { ...item, ...patch } : item,
  );
  items.value = next;
}

function addItem() {
  items.value = [
    ...items.value,
    {
      level: 'A',
      itemType: 'short_answer',
      prompt: '',
      options: [],
      answer: '',
      analysis: '',
    },
  ];
}

function removeItem(index: number) {
  items.value = items.value.filter((_, i) => i !== index);
}

function updateOption(itemIndex: number, optionIndex: number, value: string) {
  const item = items.value[itemIndex];
  const options = [...item.options];
  options[optionIndex] = value;
  updateItem(itemIndex, { options });
}

function addOption(itemIndex: number) {
  const item = items.value[itemIndex];
  updateItem(itemIndex, { options: [...item.options, ''] });
}

function removeOption(itemIndex: number, optionIndex: number) {
  const item = items.value[itemIndex];
  updateItem(itemIndex, { options: item.options.filter((_, i) => i !== optionIndex) });
}
</script>

<template>
  <div class="assessment-editor">
    <div v-for="(item, index) in items" :key="index" class="assessment-item">
      <div class="item-header">
        <select
          class="level-select"
          :value="item.level"
          :disabled="disabled"
          @change="updateItem(index, { level: ($event.target as HTMLSelectElement).value as AssessmentItem['level'] })"
        >
          <option value="A">A级</option>
          <option value="B">B级</option>
          <option value="C">C级</option>
          <option value="D">D级</option>
        </select>
        <select
          class="type-select"
          :value="item.itemType"
          :disabled="disabled"
          @change="updateItem(index, { itemType: ($event.target as HTMLSelectElement).value as AssessmentItem['itemType'] })"
        >
          <option value="short_answer">简答题</option>
          <option value="choice">选择题</option>
          <option value="fill_blank">填空题</option>
        </select>
        <button
          v-if="!disabled && items.length > 1"
          type="button"
          class="item-remove"
          title="删除"
          @click="removeItem(index)"
        >
          &times;
        </button>
      </div>
      <div class="item-body">
        <textarea
          class="item-textarea"
          :value="item.prompt"
          :disabled="disabled"
          placeholder="题目内容"
          rows="2"
          @input="updateItem(index, { prompt: ($event.target as HTMLTextAreaElement).value })"
        />
        <FormulaText
          v-if="containsFormula(item.prompt)"
          class="formula-preview"
          :text="item.prompt"
          preview
        />
        <div v-if="item.itemType === 'choice'" class="item-options">
          <div v-for="(opt, oi) in item.options" :key="oi" class="option-row">
            <span class="option-label">{{ String.fromCharCode(65 + oi) }}.</span>
            <div class="formula-field">
              <input
                type="text"
                class="option-input"
                :value="opt"
                :disabled="disabled"
                @input="updateOption(index, oi, ($event.target as HTMLInputElement).value)"
              />
              <FormulaText
                v-if="containsFormula(opt)"
                class="formula-preview"
                :text="opt"
                preview
              />
            </div>
            <button
              v-if="!disabled"
              type="button"
              class="item-remove-small"
              @click="removeOption(index, oi)"
            >
              &times;
            </button>
          </div>
          <button
            v-if="!disabled"
            type="button"
            class="add-option-btn"
            @click="addOption(index)"
          >
            + 添加选项
          </button>
        </div>
        <div class="item-answer">
          <label class="step-label">答案</label>
          <div class="formula-field">
            <input
              type="text"
              class="answer-input"
              :value="item.answer"
              :disabled="disabled"
              placeholder="参考答案"
              @input="updateItem(index, { answer: ($event.target as HTMLInputElement).value })"
            />
            <FormulaText
              v-if="containsFormula(item.answer)"
              class="formula-preview"
              :text="item.answer"
              preview
            />
          </div>
        </div>
        <div class="item-analysis">
          <label class="step-label">解析</label>
          <textarea
            class="item-textarea"
            :value="item.analysis"
            :disabled="disabled"
            placeholder="解题思路..."
            rows="2"
            @input="updateItem(index, { analysis: ($event.target as HTMLTextAreaElement).value })"
          />
          <FormulaText
            v-if="containsFormula(item.analysis)"
            class="formula-preview"
            :text="item.analysis"
            preview
          />
        </div>
      </div>
    </div>
    <button
      v-if="!disabled"
      type="button"
      class="add-item-btn"
      @click="addItem"
    >
      + 添加题目
    </button>
  </div>
</template>
