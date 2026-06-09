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

type Section = { label: string; fields: FormField[] };

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

  const sections = computed<Section[]>(() => {
    const all: FormField[] = fields.value;
    const result: Section[] = [];
    let current: FormField[] = [];
    let nextLabel = "";
    let isFirst = true;

    for (const field of all) {
      if (field.fieldtype === Fieldtype.PAGE_BREAK) {
        if (isFirst) {
          nextLabel = field.label || "Step 1";
          isFirst = false;
          continue;
        }
        result.push({
          label: nextLabel || `Step ${result.length + 1}`,
          fields: current,
        });
        current = [];
        nextLabel = field.label || "";
        continue;
      }
      isFirst = false;
      current.push(field);
    }

    result.push({
      label:
        nextLabel ||
        (result.length === 0 ? "Step 1" : `Step ${result.length + 1}`),
      fields: current,
    });

    return result;
  });

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

    // Remap distinct column_index values within each row to 0..M-1
    // (cells sharing a column_index stay grouped — multi-cell columns preserved)
    const rowColsMap = new Map<number, Set<number>>();
    for (const f of fs) {
      const r = f.row_index!;
      if (!rowColsMap.has(r)) rowColsMap.set(r, new Set());
      rowColsMap.get(r)!.add(f.column_index ?? 0);
    }
    const colRemapByRow = new Map<number, Map<number, number>>();
    for (const [r, cols] of rowColsMap) {
      const sorted = [...cols].sort((a, b) => a - b);
      colRemapByRow.set(r, new Map(sorted.map((c, i) => [c, i])));
    }
    for (const f of fs) {
      f.column_index =
        colRemapByRow.get(f.row_index!)!.get(f.column_index ?? 0) ?? 0;
    }

    // Renumber cell_index within each (row, column) to 0..K-1
    const cellMap = new Map<string, FormField[]>();
    for (const f of fs) {
      const key = `${f.row_index}-${f.column_index}`;
      if (!cellMap.has(key)) cellMap.set(key, []);
      cellMap.get(key)!.push(f);
    }
    for (const cells of cellMap.values()) {
      cells
        .sort((a, b) => (a.cell_index ?? 0) - (b.cell_index ?? 0))
        .forEach((f, i) => {
          f.cell_index = i;
        });
    }
  }

  function lastRowIndex(fs: FormField[]): number {
    return fs.reduce((m, f) => Math.max(m, f.row_index ?? 0), -1);
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

    const insertAt = getActiveSectionEndIndex();
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

    compact();
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

    compact();
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

  function getActiveSectionEndIndex(): number {
    const fs: FormField[] = formResource.value?.doc?.fields ?? [];
    if (!isMultiSection.value) return fs.length;

    let sectionIdx = 0;
    for (let i = 0; i < fs.length; i++) {
      if (fs[i].fieldtype === Fieldtype.PAGE_BREAK) {
        if (sectionIdx === activeSectionIndex.value) return i;
        sectionIdx++;
      }
    }
    return fs.length;
  }

  function addStep() {
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return;

    const count = sections.value.length;
    fs.push({
      idx: fs.length + 1,
      fieldtype: Fieldtype.PAGE_BREAK,
      label: `Step ${count + 1}`,
      fieldname: scrubFieldname(`section_${count + 1}`),
      row_index: lastRowIndex(fs) + 1,
      column_index: 0,
      cell_index: 0,
    } as FormField);

    activeSectionIndex.value = count;
  }

  function findSectionPBIndex(sectionIndex: number): number {
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return -1;
    const hasLeadingPB = fs[0]?.fieldtype === Fieldtype.PAGE_BREAK;
    const target = sectionIndex + (hasLeadingPB ? 1 : 0);
    let pbCount = 0;
    for (let i = 0; i < fs.length; i++) {
      if (fs[i].fieldtype === Fieldtype.PAGE_BREAK) {
        pbCount++;
        if (pbCount === target) return i;
      }
    }
    return -1;
  }

  function stripOrphanedLeadingPB() {
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return;
    const hasLeadingPB = fs[0]?.fieldtype === Fieldtype.PAGE_BREAK;
    const pbCount = fs.filter(
      (f) => f.fieldtype === Fieldtype.PAGE_BREAK
    ).length;
    if (hasLeadingPB && pbCount === 1) {
      fs.splice(0, 1);
    }
  }

  function removeSectionKeepFields(index: number) {
    if (index <= 0) return;
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return;

    const pbIdx = findSectionPBIndex(index);
    if (pbIdx === -1) return;

    const prevFields = sections.value[index - 1]?.fields ?? [];
    const movedFields = sections.value[index]?.fields ?? [];

    const maxPrevRow = prevFields.reduce(
      (max, f) => Math.max(max, f.row_index ?? 0),
      -1
    );
    const minMovedRow = movedFields.reduce(
      (min, f) => Math.min(min, f.row_index ?? 0),
      Infinity
    );

    if (movedFields.length > 0 && isFinite(minMovedRow)) {
      const offset = maxPrevRow - minMovedRow + 1;
      for (const f of movedFields) {
        f.row_index = (f.row_index ?? 0) + offset;
      }
    }

    fs.splice(pbIdx, 1);
    stripOrphanedLeadingPB();
    compact();
    if (activeSectionIndex.value >= sections.value.length) {
      activeSectionIndex.value = sections.value.length - 1;
    }
  }

  function removeSectionWithFields(index: number) {
    if (index <= 0) return;
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return;

    const sectionFields = sections.value[index]?.fields ?? [];
    const fieldSet = new Set(sectionFields);
    const pbIdx = findSectionPBIndex(index);

    const toRemove = new Set<number>();
    if (pbIdx !== -1) toRemove.add(pbIdx);
    for (let i = 0; i < fs.length; i++) {
      if (fieldSet.has(fs[i])) toRemove.add(i);
    }

    for (const i of [...toRemove].sort((a, b) => b - a)) {
      fs.splice(i, 1);
    }

    stripOrphanedLeadingPB();
    compact();
    if (activeSectionIndex.value >= sections.value.length) {
      activeSectionIndex.value = sections.value.length - 1;
    }
  }

  function renameSection(index: number, newLabel: string) {
    const fs: FormField[] = formResource.value?.doc?.fields;
    if (!fs) return;

    if (index === 0 && fs[0]?.fieldtype !== Fieldtype.PAGE_BREAK) {
      fs.unshift({
        idx: 0,
        fieldtype: Fieldtype.PAGE_BREAK,
        label: newLabel,
        fieldname: scrubFieldname("section_1"),
        row_index: 0,
        column_index: 0,
        cell_index: 0,
      } as FormField);
      return;
    }

    const pbIdx = findSectionPBIndex(index);
    if (pbIdx !== -1) {
      fs[pbIdx].label = newLabel;
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
    removeSectionKeepFields,
    removeSectionWithFields,
    renameSection,
    selectField,
    updateField,
    removeField,
    moveField,
    insertCell,
    insertNewRow,
  };
});
