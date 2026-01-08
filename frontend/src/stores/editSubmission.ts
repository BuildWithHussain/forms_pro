import { createDocumentResource, createResource } from "frappe-ui";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { toast } from "vue-sonner";

export const useEditSubmission = defineStore("editSubmission", () => {
  const submissionDoctype = ref<string | null>(null);
  const submissionName = ref<string | null>(null);
  const submissionResource = ref<any>(null);
  const submission = computed(() => submissionResource.value?.doc || null);
  const isDraft = computed(
    () => submission.value?.fp_submission_status == "Draft",
  );
  const isSubmitted = computed(
    () => submission.value?.fp_submission_status == "Submitted",
  );

  const isLoading = ref(true);

  async function initialize(doctype: string, name: string) {
    isLoading.value = true;
    submissionDoctype.value = doctype;
    submissionName.value = name;
    submissionResource.value = createDocumentResource({
      doctype: submissionDoctype.value,
      name: submissionName.value,
    });

    isLoading.value = false;
  }

  function convertToDraft() {
    submissionResource.value.setValue.submit(
      {
        fp_submission_status: "Draft",
      },
      {
        onSuccess: () => {
          toast.success("Submission converted to draft");
        },
        onError: () => {
          toast.error("Failed to convert submission to draft");
        },
      },
    );
  }

  function updateForm(data: Record<string, any>) {
    submissionResource.value.setValue.submit(data, {
      onSuccess: () => {
        toast.success("Submission updated");
      },
      onError: () => {
        toast.error("Failed to update submission");
      },
    });
  }

  function updateAndSubmitForm(data: Record<string, any>) {
    updateForm(data);
    submitForm();
  }

  function submitForm() {
    submissionResource.value.setValue.submit(
      {
        fp_submission_status: "Submitted",
      },
      {
        onSuccess: () => {
          toast.success("Submission submitted");
        },
        onError: () => {
          toast.error("Failed to submit submission");
        },
      },
    );
  }

  return {
    submissionResource,
    submission,
    isLoading,
    submissionDoctype,
    submissionName,
    initialize,
    isDraft,
    isSubmitted,
    convertToDraft,
    updateForm,
    updateAndSubmitForm,
    submitForm,
  };
});
