import { computed, ref, type Ref, type ComputedRef } from "vue";
import type { FormField } from "@/types/formfield";
import { groupFieldsIntoSteps, type FormStep } from "@/utils/form_steps";

export type { FormStep };

export function useFormSteps(
  allFields: Ref<FormField[]> | ComputedRef<FormField[]>
) {
  const currentStepIndex = ref(0);

  const steps = computed<FormStep[]>(() =>
    groupFieldsIntoSteps(allFields.value)
  );

  const isMultiStep = computed(() => steps.value.length > 1);

  const currentStep = computed(
    () => steps.value[currentStepIndex.value] ?? steps.value[0]
  );

  const currentStepFields = computed<FormField[]>(
    () => currentStep.value?.fields ?? []
  );

  const isFirstStep = computed(() => currentStepIndex.value === 0);
  const isLastStep = computed(
    () => currentStepIndex.value === steps.value.length - 1
  );

  const totalSteps = computed(() => steps.value.length);
  const stepDirection = ref<"forward" | "backward">("forward");

  function nextStep() {
    if (!isLastStep.value) {
      stepDirection.value = "forward";
      currentStepIndex.value++;
    }
  }

  function prevStep() {
    if (!isFirstStep.value) {
      stepDirection.value = "backward";
      currentStepIndex.value--;
    }
  }

  function goToStep(index: number) {
    if (index >= 0 && index < steps.value.length) {
      stepDirection.value =
        index > currentStepIndex.value ? "forward" : "backward";
      currentStepIndex.value = index;
    }
  }

  return {
    steps,
    currentStepIndex,
    currentStep,
    currentStepFields,
    isMultiStep,
    isFirstStep,
    isLastStep,
    totalSteps,
    stepDirection,
    nextStep,
    prevStep,
    goToStep,
  };
}
