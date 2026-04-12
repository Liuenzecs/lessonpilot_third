import { computed, ref, watch, type ComputedRef } from 'vue';

export type OnboardingStep =
  | 'workspace_cta'
  | 'task_create'
  | 'editor_outline'
  | 'editor_actions';

export interface OnboardingProgress {
  version: string;
  completed_steps: OnboardingStep[];
  dismissed: boolean;
}

const ONBOARDING_VERSION = 'phase5-ux-v1';
const ONBOARDING_STEPS: OnboardingStep[] = [
  'workspace_cta',
  'task_create',
  'editor_outline',
  'editor_actions',
];

function getStorageKey(userId: string) {
  return `lessonpilot.onboarding.${userId}`;
}

function createDefaultProgress(): OnboardingProgress {
  return {
    version: ONBOARDING_VERSION,
    completed_steps: [],
    dismissed: false,
  };
}

function loadProgress(userId: string | null): OnboardingProgress {
  if (!userId || typeof window === 'undefined') {
    return createDefaultProgress();
  }

  const rawValue = localStorage.getItem(getStorageKey(userId));
  if (!rawValue) {
    return createDefaultProgress();
  }

  try {
    const parsed = JSON.parse(rawValue) as Partial<OnboardingProgress>;
    if (parsed.version !== ONBOARDING_VERSION) {
      return createDefaultProgress();
    }

    return {
      version: ONBOARDING_VERSION,
      completed_steps: Array.isArray(parsed.completed_steps)
        ? parsed.completed_steps.filter((step): step is OnboardingStep =>
            ONBOARDING_STEPS.includes(step as OnboardingStep),
          )
        : [],
      dismissed: Boolean(parsed.dismissed),
    };
  } catch {
    return createDefaultProgress();
  }
}

function persistProgress(userId: string | null, progress: OnboardingProgress) {
  if (!userId || typeof window === 'undefined') {
    return;
  }
  localStorage.setItem(getStorageKey(userId), JSON.stringify(progress));
}

export function useOnboarding(userId: ComputedRef<string | null>) {
  const progress = ref<OnboardingProgress>(createDefaultProgress());

  watch(
    userId,
    (nextUserId) => {
      progress.value = loadProgress(nextUserId);
    },
    { immediate: true },
  );

  const currentStep = computed<OnboardingStep | null>(() => {
    if (progress.value.dismissed) {
      return null;
    }

    return ONBOARDING_STEPS.find((step) => !progress.value.completed_steps.includes(step)) ?? null;
  });

  function commit(nextProgress: OnboardingProgress) {
    progress.value = nextProgress;
    persistProgress(userId.value, nextProgress);
  }

  function complete(step: OnboardingStep) {
    if (progress.value.completed_steps.includes(step)) {
      return;
    }

    commit({
      ...progress.value,
      completed_steps: [...progress.value.completed_steps, step],
      dismissed: false,
    });
  }

  function completeThrough(step: OnboardingStep) {
    const index = ONBOARDING_STEPS.indexOf(step);
    if (index < 0) {
      return;
    }

    const mergedSteps = Array.from(
      new Set([...progress.value.completed_steps, ...ONBOARDING_STEPS.slice(0, index + 1)]),
    );

    commit({
      ...progress.value,
      completed_steps: mergedSteps,
      dismissed: false,
    });
  }

  function skipAll() {
    commit({
      ...progress.value,
      dismissed: true,
    });
  }

  return {
    currentStep,
    progress: computed(() => progress.value),
    isActive(step: OnboardingStep) {
      return currentStep.value === step;
    },
    complete,
    completeThrough,
    skipAll,
  };
}
