<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

import {
  useAddEntryMutation,
  useCreateSemesterMutation,
  useDeleteEntryMutation,
  useDeleteSemesterMutation,
  useSemesterDetail,
  useSemesters,
} from '@/features/calendar/composables/useCalendar';
import type { LessonScheduleEntryRead, SemesterCreate } from '@/features/calendar/types';
import { useTasks } from '@/features/task/composables/useTasks';
import { getErrorDescription } from '@/shared/api/errors';
import { useToast } from '@/shared/composables/useToast';

const router = useRouter();
const toast = useToast();

const { data: semesters, isLoading: semestersLoading } = useSemesters();
const { data: allTasks } = useTasks(1, 100);

const selectedSemesterId = ref<string | null>(null);
const showCreateForm = ref(false);
const showAssignModal = ref(false);
const assignWeekId = ref('');
const assignDayOfWeek = ref(1);
const assignTaskId = ref('');
const assignPeriod = ref<number | null>(null);

// Init: select first semester
watch(semesters, (list) => {
  if (list?.length && !selectedSemesterId.value) {
    selectedSemesterId.value = list[0].id;
  }
}, { immediate: true });

const detailEnabled = computed(() => Boolean(selectedSemesterId.value));
const { data: semesterDetail, isLoading: detailLoading } = useSemesterDetail(selectedSemesterId, detailEnabled);

const createMutation = useCreateSemesterMutation();
const deleteMutation = useDeleteSemesterMutation();
const addEntryMutation = useAddEntryMutation(selectedSemesterId);
const deleteEntryMutation = useDeleteEntryMutation(selectedSemesterId);

const newSemester = ref<SemesterCreate>({
  name: '',
  start_date: '',
  end_date: '',
  grade: '七年级上',
  subject: '语文',
});

const dayLabels = ['', '周一', '周二', '周三', '周四', '周五'];

function getEntriesForDay(entries: LessonScheduleEntryRead[], day: number) {
  return entries.filter((e) => e.day_of_week === day).sort((a, b) => (a.class_period ?? 0) - (b.class_period ?? 0));
}

async function handleCreateSemester() {
  try {
    const result = await createMutation.mutateAsync(newSemester.value);
    selectedSemesterId.value = result.id;
    showCreateForm.value = false;
    newSemester.value = { name: '', start_date: '', end_date: '', grade: '七年级上', subject: '语文' };
    toast.success('学期已创建');
  } catch (error) {
    toast.error('创建失败', getErrorDescription(error));
  }
}

async function handleDeleteSemester() {
  if (!selectedSemesterId.value || !confirm('确定删除这个学期及所有排课数据？')) return;
  try {
    await deleteMutation.mutateAsync(selectedSemesterId.value);
    selectedSemesterId.value = null;
    toast.success('学期已删除');
  } catch (error) {
    toast.error('删除失败', getErrorDescription(error));
  }
}

function openAssignModal(weekId: string, dayOfWeek: number) {
  assignWeekId.value = weekId;
  assignDayOfWeek.value = dayOfWeek;
  assignTaskId.value = '';
  assignPeriod.value = null;
  showAssignModal.value = true;
}

async function handleAssign() {
  if (!assignTaskId.value) return;
  try {
    await addEntryMutation.mutateAsync({
      weekId: assignWeekId.value,
      payload: {
        task_id: assignTaskId.value,
        day_of_week: assignDayOfWeek.value,
        class_period: assignPeriod.value,
      },
    });
    showAssignModal.value = false;
    toast.success('已排课');
  } catch (error) {
    toast.error('排课失败', getErrorDescription(error));
  }
}

async function handleRemoveEntry(entryId: string) {
  try {
    await deleteEntryMutation.mutateAsync(entryId);
    toast.success('已移除');
  } catch (error) {
    toast.error('移除失败', getErrorDescription(error));
  }
}
</script>

<template>
  <div class="page-shell calendar-page">
    <header class="page-header">
      <button class="button ghost" type="button" @click="router.push({ name: 'tasks' })">← 返回备课台</button>
      <h1 class="page-title">教学日历</h1>
      <p class="page-subtitle">规划学期、排课管理，按周查看每日教学安排</p>
    </header>

    <div class="calendar-layout">
      <!-- Left: semester panel -->
      <aside class="calendar-sidebar">
        <div class="semester-panel">
          <h3 class="sidebar-title">学期</h3>
          <div v-if="semestersLoading" class="text-muted">加载中...</div>
          <div v-else-if="!semesters?.length && !showCreateForm" class="text-muted">
            暂无学期
          </div>
          <ul v-if="semesters?.length" class="semester-list">
            <li
              v-for="s in semesters"
              :key="s.id"
              class="semester-item"
              :class="{ active: s.id === selectedSemesterId }"
              @click="selectedSemesterId = s.id"
            >
              <span class="semester-name">{{ s.name }}</span>
              <span class="semester-meta">{{ s.grade }} · {{ s.subject }} · {{ s.week_count }}周</span>
            </li>
          </ul>
          <button v-if="!showCreateForm" class="button ghost small" type="button" @click="showCreateForm = true">
            + 新建学期
          </button>
        </div>

        <!-- Create semester form -->
        <div v-if="showCreateForm" class="create-form app-card">
          <label class="form-field">
            <span>学期名称</span>
            <input v-model="newSemester.name" class="input" placeholder="如：2026年春季学期" />
          </label>
          <label class="form-field">
            <span>开始日期</span>
            <input v-model="newSemester.start_date" class="input" type="date" />
          </label>
          <label class="form-field">
            <span>结束日期</span>
            <input v-model="newSemester.end_date" class="input" type="date" />
          </label>
          <label class="form-field">
            <span>年级</span>
            <input v-model="newSemester.grade" class="input" />
          </label>
          <div class="form-actions">
            <button class="button primary small" :disabled="createMutation.isPending.value" @click="handleCreateSemester">
              {{ createMutation.isPending.value ? '创建中...' : '创建' }}
            </button>
            <button class="button ghost small" @click="showCreateForm = false">取消</button>
          </div>
        </div>

        <button v-if="selectedSemesterId" class="button ghost danger small" style="margin-top:12px" @click="handleDeleteSemester">
          删除当前学期
        </button>
      </aside>

      <!-- Main: week grid -->
      <main class="calendar-main">
        <div v-if="!selectedSemesterId" class="calendar-empty">选择一个学期或新建一个学期开始排课</div>
        <div v-else-if="detailLoading" class="calendar-empty">加载中...</div>
        <div v-else-if="semesterDetail" class="week-grid">
          <div
            v-for="week in semesterDetail.weeks"
            :key="week.id"
            class="week-column"
          >
            <div class="week-header">
              <span class="week-number">第{{ week.week_number }}周</span>
              <span class="week-dates">{{ new Date(week.start_date).toLocaleDateString('zh-CN', { month:'short', day:'numeric' }) }} - {{ new Date(week.end_date).toLocaleDateString('zh-CN', { month:'short', day:'numeric' }) }}</span>
            </div>
            <div
              v-for="day in 5"
              :key="day"
              class="day-cell"
              @click="openAssignModal(week.id, day)"
            >
              <div class="day-label">{{ dayLabels[day] }}</div>
              <div class="day-entries">
                <div
                  v-for="entry in getEntriesForDay(week.entries, day)"
                  :key="entry.id"
                  class="entry-card"
                >
                  <div class="entry-title">{{ entry.task_title }}</div>
                  <div v-if="entry.class_period" class="entry-period">第{{ entry.class_period }}节</div>
                  <button
                    class="entry-remove"
                    type="button"
                    title="移除"
                    @click.stop="handleRemoveEntry(entry.id)"
                  >✕</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Assign modal -->
    <Teleport to="body">
      <div v-if="showAssignModal" class="modal-backdrop" @click.self="showAssignModal = false">
        <div class="modal-content app-card">
          <h3 class="modal-title">排课 — {{ dayLabels[assignDayOfWeek] }}</h3>
          <label class="form-field">
            <span>选择备课</span>
            <select v-model="assignTaskId" class="input">
              <option value="">-- 请选择 --</option>
              <option v-for="t in allTasks?.items" :key="t.id" :value="t.id">
                {{ t.title }}（{{ t.subject }} {{ t.grade }}）
              </option>
            </select>
          </label>
          <label class="form-field">
            <span>第几节（选填）</span>
            <input v-model.number="assignPeriod" class="input" type="number" min="1" max="10" />
          </label>
          <div class="form-actions">
            <button class="button primary" :disabled="!assignTaskId || addEntryMutation.isPending.value" @click="handleAssign">
              {{ addEntryMutation.isPending.value ? '排课中...' : '确认排课' }}
            </button>
            <button class="button ghost" @click="showAssignModal = false">取消</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.calendar-page {
  --calendar-sidebar-width: 240px;
}
.calendar-layout {
  display: flex;
  gap: 0;
  height: calc(100vh - 140px);
}
.calendar-sidebar {
  width: var(--calendar-sidebar-width);
  flex-shrink: 0;
  padding: 20px;
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
}
.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px;
}
.semester-list {
  list-style: none;
  padding: 0;
  margin: 0 0 12px;
}
.semester-item {
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 4px;
}
.semester-item.active {
  background: var(--color-primary-light, #e8f4f8);
}
.semester-item:hover:not(.active) {
  background: var(--color-bg);
}
.semester-name {
  display: block;
  font-size: 13px;
  font-weight: 500;
}
.semester-meta {
  font-size: 11px;
  color: var(--color-text-secondary);
}
.create-form {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 12px;
  color: var(--color-text-secondary);
}
.form-actions {
  display: flex;
  gap: 8px;
}
.calendar-main {
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
  padding: 16px;
}
.calendar-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  font-size: 14px;
}
.week-grid {
  display: flex;
  gap: 8px;
  min-width: fit-content;
  padding-bottom: 16px;
}
.week-column {
  flex: 1 1 140px;
  min-width: 140px;
  max-width: 220px;
}
.week-header {
  padding: 8px 6px;
  font-size: 12px;
  font-weight: 600;
  border-bottom: 2px solid var(--color-primary);
  margin-bottom: 6px;
  text-align: center;
}
.week-number {
  display: block;
}
.week-dates {
  font-size: 10px;
  color: var(--color-text-secondary);
  font-weight: 400;
}
.day-cell {
  min-height: 80px;
  padding: 6px;
  margin-bottom: 4px;
  border: 1px dashed var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}
.day-cell:hover {
  background: var(--color-bg);
}
.day-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}
.entry-card {
  background: var(--color-primary-light, #e8f4f8);
  padding: 6px 8px;
  border-radius: 4px;
  margin-bottom: 4px;
  position: relative;
}
.entry-title {
  font-size: 12px;
  font-weight: 500;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.entry-period {
  font-size: 10px;
  color: var(--color-text-secondary);
}
.entry-remove {
  position: absolute;
  top: 4px;
  right: 4px;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 12px;
  padding: 0 2px;
}
.entry-remove:hover {
  color: var(--color-danger);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  width: 400px;
  max-width: 90vw;
  padding: 24px;
}
.modal-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
}
.button.small {
  font-size: 12px;
  padding: 4px 10px;
}
</style>
