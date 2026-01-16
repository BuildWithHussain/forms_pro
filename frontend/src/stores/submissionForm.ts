import { createResource } from "frappe-ui";
import { toast } from "vue-sonner";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { FormField } from "@/types/formfield";
import { useStorage } from "@vueuse/core";
import { session } from "@/data/session";
import {
  shouldFieldBeRequired,
  shouldFieldBeVisible,
} from "@/utils/conditionals";

export type UserSubmission = {
  name: string;
  creation: string;
  modified: string;
};

export enum SubmissionStatus {
  DRAFT = "Draft",
  SUBMITTED = "Submitted",
}

export const useSubmissionForm = defineStore("submissionForm", () => {
  const formResource = ref<any>(null);
  const currentFormRoute = ref<string | null>(null);
  const isLoading = computed(() => formResource.value?.loading);
  const allowIncompleteForms = computed(
    () => formResource.value?.data?.allow_incomplete
  );

  const currentFormId = computed((): string | null => {
    if (!formResource.value || !formResource.value.data) {
      return null;
    }

    return formResource.value.data.name;
  });

  const formIsPublished = computed((): boolean | null => {
    if (!formResource.value || !formResource.value.data) {
      return null;
    }

    return formResource.value.data.is_published;
  });

  const errors = ref<string[]>([]);
  const inSuccessState = ref<boolean>(false);
  const inFormFillingState = ref<boolean>(true);

  const fields = ref<Record<string, any>>({});

  const userSubmissionsResource = createResource({
    url: "forms_pro.api.submission.get_user_submissions",
    makeParams() {
      return {
        form_id: currentFormId.value,
      };
    },
    auto: false,
  });

  const userSubmissions = computed((): UserSubmission[] | null => {
    if (
      userSubmissionsResource.data &&
      userSubmissionsResource.data.length > 0
    ) {
      return userSubmissionsResource.data;
    }
    return null;
  });

  function initializeFields() {
    if (!formResource.value?.data) return;

    let _fields: Record<string, any> = {};
    formResource.value.data.fields.forEach((field: FormField) => {
      _fields[field.fieldname] = "";
      if (field.default) {
        _fields[field.fieldname] = field.default;
      }
    });

    fields.value = _fields;
  }

  async function initialize(route: string) {
    currentFormRoute.value = route;
    formResource.value = createResource({
      url: "forms_pro.api.form.get_form_by_route",
      params: {
        route: route,
      },
      onSuccess(data: any) {
        // Initialize fields with defaults first
        initializeFields();

        // Use VueUse's useStorage for reactive draft data
        const draftKey = `draft_submission_data_${data.name}`;
        const draftData = useStorage(draftKey, {}, localStorage);

        if (draftData.value && Object.keys(draftData.value).length > 0) {
          // Merge draft data with initialized fields
          fields.value = { ...fields.value, ...draftData.value };
        }

        inFormFillingState.value = true;
      },
    });

    await formResource.value.fetch();
    if (session.isLoggedIn) {
      await userSubmissionsResource.fetch();
    }
  }

  function saveAsDraft() {
    toast.info("Saving draft...");
    submitForm(true, true);
  }

  async function submitForm(
    is_draft: boolean = false,
    ignore_validations: boolean = false
  ) {
    if (!ignore_validations) {
      validateValues();
      if (errors.value.length > 0) {
        return;
      }
    }

    const _submit_doc = createResource({
      url: "forms_pro.api.submission.submit_form_response",
      makeParams() {
        return {
          form_id: formResource.value.data.name,
          form_data: Object.entries(fields.value).map(([fieldname, value]) => ({
            fieldname: fieldname,
            value: value,
          })),
          submission_status: is_draft
            ? SubmissionStatus.DRAFT
            : SubmissionStatus.SUBMITTED,
        };
      },
      onSuccess() {
        clearDraft();
        if (is_draft) {
          toast.info("Draft saved successfully");
          inFormFillingState.value = true;
          userSubmissionsResource.fetch();
        } else {
          inFormFillingState.value = false;
          inSuccessState.value = true;
        }
      },
      onError(error: any) {
        toast.error("Failed to submit form");
        errors.value = error.messages?.map((message: string) => message) || [];
        if (errors.value.length === 0) {
          errors.value.push(
            "Error while submitting form. Check the values and try again."
          );
        }
      },
    });

    await _submit_doc.fetch();
  }

  function validateValues() {
    errors.value = [];
    const allFields = formResource.value.data.fields || [];

    allFields.forEach((field: FormField) => {
      // Only validate visible fields
      const isVisible = shouldFieldBeVisible(field, fields.value, allFields);
      if (!isVisible) {
        return;
      }

      // Check if field is required (including conditional requirements)
      const isRequired = shouldFieldBeRequired(field, fields.value, allFields);

      if (isRequired && !fields.value[field.fieldname]) {
        errors.value.push(`${field.label} is required`);
      }
    });
  }

  function clearDraft() {
    const draftKey = `draft_submission_data_${formResource.value.data.name}`;
    const draftData = useStorage(draftKey, {}, localStorage);
    draftData.value = {};
  }

  return {
    formResource,
    currentFormId,
    currentFormRoute,
    validateValues,
    fields,
    isLoading,
    allowIncompleteForms,
    errors,
    inSuccessState,
    inFormFillingState,
    userSubmissionsResource,
    userSubmissions,
    formIsPublished,
    initialize,
    submitForm,
    saveAsDraft,
  };
});
