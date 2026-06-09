import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { createDocumentResource, createResource } from "frappe-ui";
import {
  mapDoctypeFieldForForm,
  scrubFieldname,
  lastRowIndex,
  compact,
} from "@/utils/form_fields";
import {
  groupFieldsIntoSteps,
  getActiveStepEndIndex,
  appendStep,
  removeStepKeepFields as removeStepKeepFieldsUtil,
  removeStepWithFields as removeStepWithFieldsUtil,
  renameStep as renameStepUtil,
  type FormStep,
} from "@/utils/form_steps";
import { FormField, Fieldtype } from "@/types/formfield";
import { Form } from "@/types/form";
import { toast } from "vue-sonner";
import { dialog } from "@/utils/dialog";

export const useEditForm = defineStore("editForm", () => {
  const formResource = ref<any>(null);
  const currentFormId = ref<string | null>(null);
  const selectedField = ref<FormField | null>(null);
  const activeSectionIndex = ref(0);
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

  const sections = computed<FormStep[]>(() =>
    groupFieldsIntoSteps(fields.value, {
      labelFallback: (n) => `Step ${n}`,
      alwaysIncludeTrailing: true,
    })
  );

  const isMultiSection = computed(() => sections.value.length > 1);

  const activeSectionFields = computed(
    () => sections.value[activeSectionIndex.value]?.fields ?? []
  );
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

  function addField(fieldtype: Fieldtype) {
    if (!formResource.value?.doc) return;
    const fs: FormField[] = formResource.value.doc.fields;

    const sectionFields = activeSectionFields.value;
    const newRowIndex =
      sectionFields.length > 0
        ? Math.max(...sectionFields.map((f) => f.row_index ?? 0)) + 1
        : 0;

    const newField: FormField = {
      idx: fs.length + 1,
      fieldtype,
      label: "",
      fieldname: "",
      options: "",
      default: "",
      description: "",
      row_index: newRowIndex,
      column_index: 0,
      cell_index: 0,
    };

    const insertAt = getActiveStepEndIndex(
      fs,
      activeSectionIndex.value,
      isMultiSection.value
    );
    fs.splice(insertAt, 0, newField);
  }

  function addFieldFromDoctype(field: any) {
    if (!formResource.value?.doc) return;
    const fs: FormField[] = formResource.value.doc.fields;

    const _newField: FormField = {
      idx: fs.length + 1,
      fieldtype: field.fieldtype,
      label: field.label,
      fieldname: field.fieldname,
      options: field.options,
      default: field.default,
      description: field.description,
      row_index: lastRowIndex(fs) + 1,
      column_index: 0,
      cell_index: 0,
    };

    fs.push(_newField);
  }

  function moveField(field: FormField, targetRow: number, targetCol: number) {
    const fs: FormField[] = formResource.value?.doc?.fields ?? [];
    if (!fs.includes(field)) return;

    // Shift existing columns in target row to open a slot (whole columns shift,
    // multi-cell columns stay grouped because all their cells share column_index)
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
    field.cell_index = 0;

    compact(fs);
  }

  function insertCell(
    field: FormField,
    targetRow: number,
    targetCol: number,
    atCell: number
  ) {
    const fs: FormField[] = formResource.value?.doc?.fields ?? [];
    if (!fs.includes(field)) return;

    // Shift cells at or below atCell within (targetRow, targetCol) down by 1
    for (const f of fs) {
      if (
        f !== field &&
        (f.row_index ?? 0) === targetRow &&
        (f.column_index ?? 0) === targetCol &&
        (f.cell_index ?? 0) >= atCell
      ) {
        f.cell_index = (f.cell_index ?? 0) + 1;
      }
    }

    field.row_index = targetRow;
    field.column_index = targetCol;
    field.cell_index = atCell;

    compact(fs);
  }

  function insertNewRow(field: FormField, atRow: number) {
    const fs: FormField[] = formResource.value?.doc?.fields ?? [];
    if (!fs.includes(field)) return;

    // Push all rows at or below atRow down by 1
    for (const f of fs) {
      if (f !== field && (f.row_index ?? 0) >= atRow) {
        f.row_index = (f.row_index ?? 0) + 1;
      }
    }

    field.row_index = atRow;
    field.column_index = 0;
    field.cell_index = 0;

    compact(fs);
  }

  function removeField(field: FormField) {
    if (formResource.value?.doc?.fields) {
      formResource.value.doc.fields = formResource.value.doc.fields.filter(
        (f: FormField) => f !== field
      );
      compact(formResource.value.doc.fields);
    }
  }

  function clampActiveStep() {
    if (activeSectionIndex.value >= sections.value.length) {
      activeSectionIndex.value = sections.value.length - 1;
    }
  }

  function addStep() {
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return;

    const count = sections.value.length;
    appendStep(fs, count);
    activeSectionIndex.value = count;
  }

  function removeStepKeepFields(index: number) {
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return;
    removeStepKeepFieldsUtil(fs, sections.value, index);
    clampActiveStep();
  }

  function removeStepWithFields(index: number) {
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return;
    removeStepWithFieldsUtil(fs, sections.value, index);
    clampActiveStep();
  }

  function renameStep(index: number, newLabel: string) {
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return;
    renameStepUtil(fs, index, newLabel);
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
    sections,
    isMultiSection,
    activeSectionFields,
    activeSectionIndex,

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
    addStep,
    removeStepKeepFields,
    removeStepWithFields,
    renameStep,
    selectField,
    updateField,
    removeField,
    moveField,
    insertCell,
    insertNewRow,
  };
});
