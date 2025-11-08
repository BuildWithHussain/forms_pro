import { createResource } from "frappe-ui";
import { toast } from "vue-sonner";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { FormField } from "@/types/formfield";
import { useStorage } from "@vueuse/core";
import { session } from "@/data/session";

export const useSubmissionForm = defineStore("submissionForm", () => {
  const formResource = ref<any>(null);
  const currentFormId = ref<string | null>(null);
  const isLoading = computed(() => formResource.value?.loading);
  const allowIncompleteForms = computed(
    () => formResource.value?.data?.allow_incomplete ,
  );

  const errors = ref<string[]>([]);
  const successSubmission = ref<number>(0);
  const inFormSubmission = ref<number>(1);

  const fields = ref<Record<string, any>>({});

  function initializeFields() {
    if (!formResource.value?.data) return;

    let _fields: Record<string, any> = {};
    formResource.value.data.fields.forEach((field: FormField) => {
      // Table fields should be initialized as empty arrays
      if (field.fieldtype === "Table") {
        _fields[field.fieldname] = [];
      } else {
        _fields[field.fieldname] = "";
        if (field.default) {
          _fields[field.fieldname] = field.default;
        }
      }
    });

    fields.value = _fields;
  }

  async function initialize(route: string) {
    // Validate route parameter
    if (!route || typeof route !== "string" || route.trim() === "") {
      console.error("[SubmissionForm] Invalid route parameter:", route);
      return;
    }
    
    currentFormId.value = route;
    formResource.value = createResource({
      url: "forms_pro.api.form.get_form_by_route",
      makeParams: () => ({
        route: route,
      }),
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

  // Helper function to convert File to base64
  async function fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = reader.result as string;
        resolve(result);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async function submitForm() {
    validateValues();
    if (errors.value.length > 0) {
      return;
    }

    // Check if guest uploads are allowed
    const isGuest = !session.isLoggedIn || session.user === "Guest";
    const formData = formResource.value?.data;
    
    if (isGuest && formData?.login_required) {
      toast.error("You must login to submit this form");
      return;
    }
    
    if (isGuest && !formData?.allow_anonymous) {
      toast.error("Anonymous submissions are not allowed for this form");
      return;
    }

    // Process form data and convert File objects to base64
    const processedFormData = await Promise.all(
      Object.entries(fields.value).map(async ([fieldname, value]) => {
        // Check if this field is a file upload field
        const field = formData?.fields?.find((f: FormField) => f.fieldname === fieldname);
        const isFileField = field && (field.fieldtype === "File Uploader" || field.fieldtype === "Attach" || field.fieldtype === "Attach Image");
        
        // If value is a File object, convert to base64
        if (value instanceof File) {
          try {
            const base64Value = await fileToBase64(value);
            return {
              fieldname: fieldname,
              value: base64Value,
            };
          } catch (error) {
            console.error("Error converting file to base64:", error);
            toast.error("Error processing file. Please try again.");
            throw error;
          }
        }
        
        // If value is already a base64 string (data:...), pass as is
        if (isFileField && typeof value === "string" && value.startsWith("data:")) {
          return {
            fieldname: fieldname,
            value: value,
          };
        }
        
        // For non-file values, pass as is
        return {
          fieldname: fieldname,
          value: value,
        };
      })
    );

    const _submit_doc = createResource({
      url: "forms_pro.api.submission.submit_form_response",
      makeParams() {
        return {
          form_id: formResource.value.data.name,
          form_data: processedFormData,
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
      if (field.reqd) {
        const value = fields.value[field.fieldname];
        // For Table fields, check if array is empty
        if (field.fieldtype === "Table") {
          if (!value || !Array.isArray(value) || value.length === 0) {
            errors.value.push(`${field.label} is required`);
          }
        } else {
          // For other fields, check if value is empty
          if (!value || (typeof value === "string" && value.trim() === "")) {
            errors.value.push(`${field.label} is required`);
          }
        }
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
