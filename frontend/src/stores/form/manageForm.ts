import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { createResource, useDoc } from "frappe-ui";
import { toast } from "vue-sonner";
// @ts-ignore
import { sessionUser } from "@/data/session";

export type PermissionTypes = "read" | "write" | "share" | "submit";

export type AccessPermissions = {
  read: boolean;
  write: boolean;
  share: boolean;
  submit: boolean;
};

export type SharedAccessUser = {
  full_name: string;
  user_image: string;
  email: string;
  read: boolean;
  write: boolean;
  share: boolean;
  submit: boolean;
};

export const useManageForm = defineStore("manageForm", () => {
  const currentFormId = ref<string>("");
  const formData = computed(() => formResource.value?.doc || null);
  const formFields = computed(() => formResource.value?.doc?.fields || []);
  const formResource = ref<any>(null);
  const formOwner = computed(() => formResource.value?.doc?.owner || null);
  const sharedAccessUsers = computed<SharedAccessUser[]>(
    () => formAccessResource.data || []
  );

  // Check if the current user has share access to the form
  const userHasShareAccess = computed<boolean>(
    () =>
      formAccessResource.data?.find(
        (user: SharedAccessUser) => user.email === sessionUser()
      )?.share ?? false
  );

  const formAccessResource = createResource({
    url: "forms_pro.api.form.get_form_shared_with",
    method: "GET",
    makeParams() {
      return {
        form_id: currentFormId.value,
      };
    },
  });

  async function initialize(formId: string) {
    currentFormId.value = formId;
    formResource.value = useDoc({
      doctype: "Form",
      name: formId,
    });
    formAccessResource.fetch();
  }

  /**
   * Add access to the form for a user
   * @param userId - The ID of the user to add access to
   * @param access - The access permissions to add (read, write, share, submit)
   */
  function addAccess(userId: string, access: AccessPermissions) {
    const _access = createResource({
      url: "frappe.share.add",
      method: "POST",
      makeParams() {
        return {
          doctype: "Form",
          name: currentFormId.value,
          user: userId,
          read: Boolean(access.read),
          write: Boolean(access.write),
          share: Boolean(access.share),
          submit: Boolean(access.submit),
        };
      },
      onSuccess() {
        formAccessResource.reload();
        toast.success("Access added successfully");
      },
      onError(error: Error) {
        toast.error("Failed to give access to the user", {
          description: error.message,
        });
      },
    });
    _access.submit();
  }

  /**
   * Set a permission for a user
   * @param userId - The ID of the user to set the permission for
   * @param permission - The permission to set (read, write, share, submit)
   * @param value - The value of the permission (true or false)
   */
  function setPermission(
    userId: string,
    permission: PermissionTypes,
    value: boolean
  ) {
    const _permission = createResource({
      url: "frappe.share.set_permission",
      method: "POST",
      makeParams() {
        return {
          doctype: "Form",
          name: currentFormId.value,
          user: userId,
          permission_to: permission,
          value: value ? 1 : 0,
        };
      },
      onSuccess() {
        formAccessResource.reload();
        toast.success("Permission set successfully");
      },
      onError(error: Error) {
        toast.error("Failed to set permission", {
          description: error.message,
        });
      },
    });
    _permission.submit();
  }

  function removeAccess(userEmail: string) {
    const _removeAccess = createResource({
      url: "forms_pro.api.form.remove_form_access",
      method: "DELETE",
      makeParams() {
        return {
          form_id: currentFormId.value,
          user_email: userEmail,
        };
      },
      onSuccess() {
        formAccessResource.reload();
        toast.success("Access removed successfully");
      },
      onError(error: Error) {
        toast.error("Failed to remove access", {
          description: error.message,
        });
      },
    });
    _removeAccess.submit();
  }

  return {
    initialize,
    addAccess,
    setPermission,
    removeAccess,
    userHasShareAccess,
    formOwner,
    sharedAccessUsers,
    currentFormId,
    formData,
    formFields,
    formResource,
    formAccessResource,
  };
});
