import { createDocumentResource } from "frappe-ui";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { toast } from "vue-sonner";

export const useEditSubmission = defineStore("editSubmission", () => {
  const submissionDoctype = ref<string | null>(null);
  const submissionName = ref<string | null>(null);
  const submissionResource = ref<any>(null);
  const submission = computed(() => submissionResource.value?.doc || null);
  const isDraft = computed(
    () => submission.value?.fp_submission_status == "Draft"
  );
  const isSubmitted = computed(
    () => submission.value?.fp_submission_status == "Submitted"
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
      }
    );
  }

  function updateForm(data: Record<string, any>): Promise<void> {
    return new Promise((resolve, reject) => {
      submissionResource.value.setValue.submit(data, {
        onSuccess: () => {
          toast.success("Your response has been updated");
          resolve();
        },
        onError: () => {
          toast.error("Failed to update your response!");
          reject(new Error("Failed to update submission"));
        },
      });
    });
  }

  async function updateAndSubmitForm(data: Record<string, any>) {
    try {
      await updateForm(data);
      submitForm();
    } catch (error) {
      // Error already handled in updateForm's onError callback
      console.error("Error updating form before submission:", error);
    }
  }

  function submitForm() {
    submissionResource.value.setValue.submit(
      {
        fp_submission_status: "Submitted",
      },
      {
        onSuccess: () => {
          toast.success("Successfully submitted your response!");
        },
        onError: () => {
          toast.error("Failed to submit!");
        },
      }
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
