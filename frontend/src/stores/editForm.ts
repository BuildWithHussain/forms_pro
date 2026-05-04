import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { createDocumentResource, createResource } from "frappe-ui";
import { mapDoctypeFieldForForm } from "@/utils/form_fields";
import { FormField, Fieldtype } from "@/types/formfield";
import { Form } from "@/types/form";
import { toast } from "vue-sonner";
import { dialog } from "@/utils/dialog";

function scrubFieldname(label: string) {
  return label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_") // replace non-alphanumeric with underscores
    .replace(/^_+|_+$/g, "") // trim leading/trailing underscores
    .replace(/_{2,}/g, "_"); // collapse multiple underscores
}

export const useEditForm = defineStore("editForm", () => {
  const formResource = ref<any>(null);
  const currentFormId = ref<string | null>(null);
  const selectedField = ref<FormField | null>(null);
  const isUnsaved = computed(() => formResource.value?.isDirty || false);
  const isLoading = computed(() => formResource.value?.loading || false);
  const isSaving = computed(
    () => formResource.value?.setValue?.loading || false
  );
  const isPublished = computed(
    () => formResource.value?.doc?.is_published || false
  );

  const doctypeFields = ref<any>([]);

  const isError = computed(() => formResource.value?.error || false);
  const formData = computed(() => formResource.value?.doc || null);
  const fields = computed(() => {
    return formResource.value?.doc?.fields || [];
  });
  const originalFormData = computed(
    () => formResource.value?.originalDoc || null
  );

  async function getDoctypeFields() {
    if (formResource.value?.doc?.linked_doctype) {
      const _fields = createResource({
        url: "forms_pro.api.form.get_doctype_fields",
        method: "GET",
        makeParams() {
          return {
            doctype: formResource.value?.doc?.linked_doctype,
          };
        },
        transform: (data: any) => {
          return data.map((field: any) => {
            return {
              ...field,
              fieldtype: mapDoctypeFieldForForm(field.fieldtype),
            };
          });
        },
      });

      await _fields.fetch();
      doctypeFields.value = _fields.data;
    }
  }

  function initialize(formId: string) {
    if (formId !== currentFormId.value) {
      currentFormId.value = formId;
      formResource.value = createDocumentResource({
        doctype: "Form",
        name: formId,
        transform: (doc: Form) => {
          return {
            ...doc,
            title: doc.title === "Untitled Form" ? "" : doc.title,
          };
        },
        onSuccess: () => {
          getDoctypeFields();
        },
      });
    }
  }

  function reload() {
    if (formResource.value) {
      formResource.value.reload();
    }
  }

  function reset() {
    currentFormId.value = null;
    formResource.value = null;
  }

  function findDuplicateFieldnames(): { label: string; fieldname: string }[] {
    const allFields = formResource.value?.doc?.fields || [];
    const seen = new Map<string, FormField>();
    const duplicates: { label: string; fieldname: string }[] = [];

    for (const field of allFields) {
      const name = field.fieldname?.trim()
        ? field.fieldname
        : scrubFieldname(field.label);

      if (seen.has(name)) {
        const existing = seen.get(name)!;
        if (!duplicates.some((d) => d.fieldname === name)) {
          duplicates.push({ label: existing.label, fieldname: name });
        }
        duplicates.push({ label: field.label, fieldname: name });
      }
      seen.set(name, field);
    }

    return duplicates;
  }

  async function save() {
    if (!isUnsaved.value) {
      toast.info("No changes to save");
      return;
    }

    if (!formResource.value) {
      toast.error("No form resource available");
      return Promise.reject(new Error("No form resource available"));
    }

    const duplicates = findDuplicateFieldnames();
    if (duplicates.length > 0) {
      const fieldList = duplicates
        .map((d) => `<b>${d.label} (${d.fieldname})</b>`)
        .join(", ");
      await dialog.alert({
        title: "Duplicate Fieldnames",
        message: `These fields will have duplicate fieldnames: ${fieldList}. Please change one of the labels or set a unique fieldname.`,
        html: true,
      });
      return Promise.reject(new Error("Duplicate fieldnames"));
    }

    formResource.value.doc.fields.forEach((field: FormField, index: number) => {
      field.idx = index + 1;
      if (!field.fieldname || field.fieldname.trim() === "") {
        field.fieldname = scrubFieldname(field.label);
      }
    });

    return formResource.value.setValue.submit(formResource.value.doc, {
      onSuccess: () => {
        toast.success("Form Updated Successfully");
      },
      onError: (error: any) => {
        toast.error("Failed to Update Form", {
          description: error.message,
        });
      },
    });
  }

  function saveAndPublish() {
    if (formResource.value) {
      formResource.value.doc.is_published = 1;
      return save();
    }
  }

  function togglePublish() {
    if (!formResource.value?.doc) return Promise.resolve();
    return formResource.value.setValue.submit(
      {
        is_published: !formResource.value.doc.is_published,
      },
      {
        onSuccess: () => {
          if (formResource.value.doc.is_published) {
            toast.success("Form published successfully");
          } else {
            toast.info("Form unpublished successfully");
          }
        },
        onError: () => {
          toast.error("Failed to publish form");
        },
      }
    );
  }

  function updateFormData(data: Partial<Form>) {
    if (formResource.value?.doc) {
      Object.assign(formResource.value.doc, data);
    }
  }

  function compact() {
    const fs: FormField[] = formResource.value?.doc?.fields ?? [];
    if (!fs.length) return;

    // Remap row_index values to 0..N-1 (closes gaps left by deletions/moves)
    const distinctRows = [...new Set(fs.map((f) => f.row_index ?? 0))].sort(
      (a, b) => a - b
    );
    const rowRemap = new Map(distinctRows.map((r, i) => [r, i]));
    for (const f of fs) {
      f.row_index = rowRemap.get(f.row_index ?? 0) ?? 0;
    }

    // Renumber column_index within each row to 0..M-1
    const rowMap = new Map<number, FormField[]>();
    for (const f of fs) {
      const r = f.row_index!;
      if (!rowMap.has(r)) rowMap.set(r, []);
      rowMap.get(r)!.push(f);
    }
    for (const row of rowMap.values()) {
      row
        .sort((a, b) => (a.column_index ?? 0) - (b.column_index ?? 0))
        .forEach((f, i) => {
          f.column_index = i;
        });
    }
  }

  function addField(fieldtype: Fieldtype) {
    if (formResource.value?.doc) {
      const fs: FormField[] = formResource.value.doc.fields;
      const lastRow =
        fs.length > 0 ? Math.max(...fs.map((f) => f.row_index ?? 0)) : -1;

      const newField: FormField = {
        idx: fs.length + 1,
        fieldtype,
        label: "",
        fieldname: "",
        options: "",
        default: "",
        description: "",
        row_index: lastRow + 1,
        column_index: 0,
      };

      fs.push(newField);
    }
  }

  function addFieldFromDoctype(field: any) {
    const fs: FormField[] = formResource.value.doc.fields;
    const lastRow =
      fs.length > 0 ? Math.max(...fs.map((f) => f.row_index ?? 0)) : -1;

    const _newField: FormField = {
      idx: fs.length + 1,
      fieldtype: field.fieldtype,
      label: field.label,
      fieldname: field.fieldname,
      options: field.options,
      default: field.default,
      description: field.description,
      row_index: lastRow + 1,
      column_index: 0,
    };

    fs.push(_newField);
  }

  function moveField(field: FormField, targetRow: number, targetCol: number) {
    const fs: FormField[] = formResource.value?.doc?.fields ?? [];

    // Shift existing columns in target row to open a slot
    for (const f of fs) {
      if (
        f !== field &&
        (f.row_index ?? 0) === targetRow &&
        (f.column_index ?? 0) >= targetCol
      ) {
        f.column_index = (f.column_index ?? 0) + 1;
      }
    }

    field.row_index = targetRow;
    field.column_index = targetCol;

    compact();
  }

  function insertNewRow(field: FormField, atRow: number) {
    const fs: FormField[] = formResource.value?.doc?.fields ?? [];

    // Push all rows at or below atRow down by 1
    for (const f of fs) {
      if (f !== field && (f.row_index ?? 0) >= atRow) {
        f.row_index = (f.row_index ?? 0) + 1;
      }
    }

    field.row_index = atRow;
    field.column_index = 0;

    compact();
  }

  function removeField(field: FormField) {
    if (formResource.value?.doc?.fields) {
      formResource.value.doc.fields = formResource.value.doc.fields.filter(
        (f: FormField) => f !== field
      );
      compact();
    }
  }

  function selectField(field: FormField | null) {
    selectedField.value = field;
  }

  function updateField(originalField: FormField, updatedField: FormField) {
    if (formResource.value?.doc?.fields) {
      const fieldIndex = formResource.value.doc.fields.findIndex(
        (f: FormField) => f === originalField
      );
      if (fieldIndex !== -1) {
        formResource.value.doc.fields[fieldIndex] = updatedField;
      }
    }
  }

  return {
    // State
    currentFormId,
    formResource,
    isUnsaved,

    // Computed
    originalFormData,
    isLoading,
    isSaving,
    isError,
    formData,
    fields,
    selectedField,
    isPublished,
    doctypeFields,

    // Actions
    initialize,
    reload,
    reset,
    save,
    saveAndPublish,
    togglePublish,
    updateFormData,
    addField,
    addFieldFromDoctype,
    selectField,
    updateField,
    removeField,
    moveField,
    insertNewRow,
  };
});
