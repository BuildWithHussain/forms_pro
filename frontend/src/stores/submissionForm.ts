import { createResource } from "frappe-ui";
import { toast } from "vue-sonner";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { FormField } from "@/types/formfield";
import { useStorage } from "@vueuse/core";

export const useSubmissionForm = defineStore("submissionForm", () => {
  const formResource = ref<any>(null);
  const currentFormId = ref<string | null>(null);
  const isLoading = computed(() => formResource.value?.loading);
  const allowIncompleteForms = computed(
    () => formResource.value?.data?.allow_incomplete
  );

  const errors = ref<string[]>([]);
  const successSubmission = ref<number>(0);
  const inFormSubmission = ref<number>(1);

  const fields = ref<Record<string, any>>({});

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
    currentFormId.value = route;
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

        inFormSubmission.value = 1;
      },
    });
    await formResource.value.fetch();
  }

  function saveAsDraft() {
    errors.value = [];

    if (!formResource.value?.data?.name) {
      toast.error("Form not loaded");
      return;
    }

    const draftKey = `draft_submission_data_${formResource.value.data.name}`;
    const draftData = useStorage(draftKey, {}, localStorage);
    draftData.value = fields.value;
    toast.success("Draft saved successfully");
  }

  async function submitForm() {
    validateValues();
    if (errors.value.length > 0) {
      return;
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
        };
      },
      onSuccess() {
        clearDraft();
        inFormSubmission.value = 0;
        successSubmission.value = 1;
      },
    });

    await _submit_doc.fetch();
  }

  function validateValues() {
    errors.value = [];
    formResource.value.data.fields.forEach((field: FormField) => {
      if (field.reqd && !fields.value[field.fieldname]) {
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
    fields,
    isLoading,
    allowIncompleteForms,
    errors,
    successSubmission,
    inFormSubmission,
    initialize,
    submitForm,
    saveAsDraft,
  };
});
