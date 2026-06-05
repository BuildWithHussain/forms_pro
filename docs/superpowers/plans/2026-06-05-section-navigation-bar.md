# Section Navigation Bar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a section navigation bar to the form builder that lets users organize form fields into sections (backed by Page Break fields) and edit the success page inline.

**Architecture:** Sections are derived from Page Break field positions in the flat fields array. A Page Break marks the start of a new section; its `label` stores the section name. The first section is implicit ("Section 1") when no Page Break exists at position 0. A new `SectionBar` component sits between the header and canvas. The `editForm` store gains section-aware computed properties and actions. The canvas filters fields to the active section, and shows a success editor when the Success tab is selected.

**Tech Stack:** Vue 3, Pinia, TypeScript, frappe-ui, vuedraggable, Tailwind CSS

---

## File Map

| Action | File | Responsibility |
|--------|------|---------------|
| Modify | `frontend/src/stores/editForm.ts` | Add section state, computed properties, and actions |
| Modify | `frontend/src/layouts/FormBuilderLayout.vue` | Insert SectionBar between header and content row |
| Modify | `frontend/src/components/FormBuilderContent.vue` | Use `activeSectionFields` for canvas, add success editor view |
| Modify | `frontend/src/components/builder/sidebar/SettingsSection.vue` | Remove Success Page editor section |
| Create | `frontend/src/components/builder/SectionBar.vue` | Section tab bar component |

---

### Task 1: Add section derivation and state to editForm store

**Files:**
- Modify: `frontend/src/stores/editForm.ts`

This task adds all the section logic to the store. The UI tasks that follow will consume these properties and actions.

- [ ] **Step 1: Add `Section` type and `activeSectionIndex` state**

At the top of the store setup function (after line 21), add:

```typescript
const activeSectionIndex = ref(0);
```

Above the store definition (after the `scrubFieldname` function, before `export const useEditForm`), add the Section type:

```typescript
export type Section = {
  name: string;
  fields: FormField[];
  pageBreak: FormField | null;
};
```

- [ ] **Step 2: Add `sections` computed property**

After the `fields` computed (line 37), add:

```typescript
const sections = computed<Section[]>(() => {
  const allFields: FormField[] = formResource.value?.doc?.fields || [];
  const result: Section[] = [];
  let currentFields: FormField[] = [];
  let currentName = "Section 1";
  let currentPageBreak: FormField | null = null;

  for (const field of allFields) {
    if (field.fieldtype === Fieldtype.PAGE_BREAK) {
      if (currentFields.length === 0 && result.length === 0) {
        currentName = field.label || "Section 1";
        currentPageBreak = field;
      } else {
        result.push({
          name: currentName,
          fields: currentFields,
          pageBreak: currentPageBreak,
        });
        currentName = field.label || `Section ${result.length + 1}`;
        currentPageBreak = field;
        currentFields = [];
      }
    } else {
      currentFields.push(field);
    }
  }
  result.push({
    name: currentName,
    fields: currentFields,
    pageBreak: currentPageBreak,
  });

  return result;
});

const activeSectionFields = computed<FormField[]>(() => {
  const sec = sections.value[activeSectionIndex.value];
  return sec?.fields ?? [];
});

const isSuccessActive = computed(() => activeSectionIndex.value === -1);
```

- [ ] **Step 3: Add `setActiveSection` action**

```typescript
function setActiveSection(index: number) {
  activeSectionIndex.value = index;
  selectedField.value = null;
}
```

- [ ] **Step 4: Add `addSection` action**

This inserts a Page Break field at the end of the fields array and switches to the new section.

```typescript
function addSection() {
  if (!formResource.value?.doc) return;
  const fs: FormField[] = formResource.value.doc.fields;
  const newSectionIndex = sections.value.length;
  const newPageBreak: FormField = {
    idx: fs.length + 1,
    fieldtype: Fieldtype.PAGE_BREAK,
    label: `Section ${newSectionIndex + 1}`,
    fieldname: `section_${newSectionIndex + 1}`,
    options: "",
    default: "",
    description: "",
    row_index: lastRowIndex(fs) + 1,
    column_index: 0,
    cell_index: 0,
  };
  fs.push(newPageBreak);
  activeSectionIndex.value = newSectionIndex;
  selectedField.value = null;
}
```

- [ ] **Step 5: Add `renameSection` action**

```typescript
function renameSection(index: number, name: string) {
  if (!formResource.value?.doc) return;
  const fs: FormField[] = formResource.value.doc.fields;
  const section = sections.value[index];
  if (!section) return;

  if (section.pageBreak) {
    section.pageBreak.label = name;
    section.pageBreak.fieldname = scrubFieldname(name);
  } else {
    const firstNonPBIndex = fs.findIndex(
      (f) => f.fieldtype !== Fieldtype.PAGE_BREAK
    );
    const insertAt = firstNonPBIndex === -1 ? 0 : firstNonPBIndex;
    const newPB: FormField = {
      idx: 0,
      fieldtype: Fieldtype.PAGE_BREAK,
      label: name,
      fieldname: scrubFieldname(name),
      options: "",
      default: "",
      description: "",
      row_index: 0,
      column_index: 0,
      cell_index: 0,
    };
    fs.splice(insertAt, 0, newPB);
    compact();
  }
}
```

- [ ] **Step 6: Add `deleteSection` action**

```typescript
function deleteSection(index: number, mergeFields: boolean) {
  if (!formResource.value?.doc) return;
  if (index === 0 && sections.value.length === 1) return;

  const section = sections.value[index];
  if (!section) return;

  const fs: FormField[] = formResource.value.doc.fields;

  if (mergeFields) {
    if (section.pageBreak) {
      formResource.value.doc.fields = fs.filter(
        (f: FormField) => f !== section.pageBreak
      );
    }
  } else {
    const toRemove = new Set<FormField>(section.fields);
    if (section.pageBreak) toRemove.add(section.pageBreak);
    formResource.value.doc.fields = fs.filter(
      (f: FormField) => !toRemove.has(f)
    );
  }

  compact();

  if (activeSectionIndex.value >= sections.value.length) {
    activeSectionIndex.value = Math.max(0, sections.value.length - 1);
  }
  selectedField.value = null;
}
```

- [ ] **Step 7: Add `reorderSections` action**

```typescript
function reorderSections(fromIndex: number, toIndex: number) {
  if (!formResource.value?.doc) return;
  if (fromIndex === toIndex) return;

  const secs = sections.value;
  if (fromIndex < 0 || fromIndex >= secs.length) return;
  if (toIndex < 0 || toIndex >= secs.length) return;

  const ordered: FormField[] = [];
  const reordered = [...secs];
  const [moved] = reordered.splice(fromIndex, 1);
  reordered.splice(toIndex, 0, moved);

  for (let i = 0; i < reordered.length; i++) {
    const sec = reordered[i];
    if (sec.pageBreak) {
      ordered.push(sec.pageBreak);
    }
    ordered.push(...sec.fields);
  }

  formResource.value.doc.fields = ordered;
  compact();
  activeSectionIndex.value = toIndex;
}
```

- [ ] **Step 8: Modify `addField` to insert into active section**

Replace the current `addField` function (lines 248-267) with:

```typescript
function addField(fieldtype: Fieldtype) {
  if (formResource.value?.doc) {
    const fs: FormField[] = formResource.value.doc.fields;
    const sectionFields = activeSectionFields.value;

    const newField: FormField = {
      idx: fs.length + 1,
      fieldtype,
      label: "",
      fieldname: "",
      options: "",
      default: "",
      description: "",
      row_index: lastRowIndex(sectionFields) + 1,
      column_index: 0,
      cell_index: 0,
    };

    const section = sections.value[activeSectionIndex.value];
    if (!section) {
      fs.push(newField);
      return;
    }

    const lastFieldInSection =
      section.fields.length > 0
        ? section.fields[section.fields.length - 1]
        : section.pageBreak;
    const insertAfterIdx = lastFieldInSection
      ? fs.indexOf(lastFieldInSection) + 1
      : fs.length;

    fs.splice(insertAfterIdx, 0, newField);
    compact();
  }
}
```

- [ ] **Step 9: Modify `addFieldFromDoctype` similarly**

Replace the current `addFieldFromDoctype` function (lines 269-287) with:

```typescript
function addFieldFromDoctype(field: any) {
  if (!formResource.value?.doc) return;
  const fs: FormField[] = formResource.value.doc.fields;
  const sectionFields = activeSectionFields.value;

  const _newField: FormField = {
    idx: fs.length + 1,
    fieldtype: field.fieldtype,
    label: field.label,
    fieldname: field.fieldname,
    options: field.options,
    default: field.default,
    description: field.description,
    row_index: lastRowIndex(sectionFields) + 1,
    column_index: 0,
    cell_index: 0,
  };

  const section = sections.value[activeSectionIndex.value];
  if (!section) {
    fs.push(_newField);
    return;
  }

  const lastFieldInSection =
    section.fields.length > 0
      ? section.fields[section.fields.length - 1]
      : section.pageBreak;
  const insertAfterIdx = lastFieldInSection
    ? fs.indexOf(lastFieldInSection) + 1
    : fs.length;

  fs.splice(insertAfterIdx, 0, _newField);
  compact();
}
```

- [ ] **Step 10: Export new state, computed properties, and actions**

Add to the return statement (after line 414):

```typescript
// Section state
activeSectionIndex,

// Section computed
sections,
activeSectionFields,
isSuccessActive,

// Section actions
setActiveSection,
addSection,
renameSection,
deleteSection,
reorderSections,
```

- [ ] **Step 11: Run typecheck**

Run: `cd frontend && yarn typecheck`
Expected: PASS (no type errors)

- [ ] **Step 12: Commit**

```bash
git add frontend/src/stores/editForm.ts
git commit -m "feat: add section derivation and management to editForm store"
```

---

### Task 2: Create SectionBar component

**Files:**
- Create: `frontend/src/components/builder/SectionBar.vue`

A simple starter component. The user will build on this further (drag-to-reorder, right-click context menu, inline rename). This version covers: clickable tabs, add section button, success tab, and basic active state styling.

- [ ] **Step 1: Create the SectionBar component**

```vue
<script setup lang="ts">
import { useEditForm } from "@/stores/editForm";
import { Plus, Check } from "@lucide/vue";

const editFormStore = useEditForm();
</script>
<template>
    <div
        class="flex items-center gap-1.5 px-4 py-2 border-b bg-surface-gray-2 overflow-x-auto"
        data-form-builder-component="section-bar"
    >
        <button
            v-for="(section, index) in editFormStore.sections"
            :key="index"
            type="button"
            class="shrink-0 rounded-md border px-3 py-1.5 text-sm transition-colors"
            :class="
                editFormStore.activeSectionIndex === index
                    ? 'border-gray-900 bg-white font-medium text-gray-900 shadow-sm'
                    : 'border-transparent text-gray-600 hover:bg-surface-gray-3 hover:text-gray-900'
            "
            @click="editFormStore.setActiveSection(index)"
        >
            {{ section.name }}
        </button>
        <button
            type="button"
            class="shrink-0 rounded-md border border-dashed border-gray-300 p-1.5 text-gray-400 hover:border-gray-400 hover:text-gray-600 transition-colors"
            @click="editFormStore.addSection()"
        >
            <Plus class="h-3.5 w-3.5" />
        </button>
        <div class="ml-auto"></div>
        <button
            type="button"
            class="shrink-0 rounded-md border px-3 py-1.5 text-sm transition-colors flex items-center gap-1.5"
            :class="
                editFormStore.isSuccessActive
                    ? 'border-gray-900 bg-white font-medium text-gray-900 shadow-sm'
                    : 'border-transparent text-gray-600 hover:bg-surface-gray-3 hover:text-gray-900'
            "
            @click="editFormStore.setActiveSection(-1)"
        >
            <Check class="h-3.5 w-3.5" />
            Success
        </button>
    </div>
</template>
```

- [ ] **Step 2: Run typecheck**

Run: `cd frontend && yarn typecheck`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/builder/SectionBar.vue
git commit -m "feat: add SectionBar component for form builder"
```

---

### Task 3: Wire SectionBar into layout and update canvas

**Files:**
- Modify: `frontend/src/layouts/FormBuilderLayout.vue`
- Modify: `frontend/src/components/FormBuilderContent.vue`

- [ ] **Step 1: Add SectionBar to FormBuilderLayout**

Replace the full content of `FormBuilderLayout.vue` with:

```vue
<script setup lang="ts">
import FormBuilderHeader from "@/components/FormBuilderHeader.vue";
import FormBuilderSidebar from "@/components/FormBuilderSidebar.vue";
import FormBuilderContent from "@/components/FormBuilderContent.vue";
import FieldEditorSidebar from "@/components/FieldEditorSidebar.vue";
import SectionBar from "@/components/builder/SectionBar.vue";
</script>
<template>
    <div class="flex flex-col">
        <FormBuilderHeader />
        <SectionBar />
        <div class="flex gap-4 justify-between">
            <FormBuilderSidebar />
            <FormBuilderContent />
            <FieldEditorSidebar />
        </div>
    </div>
</template>
```

- [ ] **Step 2: Update FormBuilderContent to use activeSectionFields**

In `FormBuilderContent.vue`, change line 30 from:

```typescript
const groupedRows = useGroupedRows(computed(() => editFormStore.fields));
```

to:

```typescript
const groupedRows = useGroupedRows(computed(() => editFormStore.activeSectionFields));
```

- [ ] **Step 3: Update the empty state check in FormBuilderContent**

Change line 195 from:

```html
<div v-if="editFormStore.fields.length === 0">
```

to:

```html
<div v-if="editFormStore.activeSectionFields.length === 0 && !editFormStore.isSuccessActive">
```

- [ ] **Step 4: Add success editor view to FormBuilderContent**

In the template, after the existing form card `div` (after line 268, before `</template>`), add the success editor. Wrap the existing form card in a `v-if="!editFormStore.isSuccessActive"` and add the success view as a sibling:

The form card div at line 172 currently starts with:
```html
<div
    v-if="editFormStore.formData"
    ref="fieldContentRef"
    class="bg-secondary min-h-[800px] max-w-screen-md w-full border rounded my-12 p-4 shadow-[0_0_10px_rgba(0,0,0,0.1)]"
>
```

Change the `v-if` to:
```html
<div
    v-if="editFormStore.formData && !editFormStore.isSuccessActive"
    ref="fieldContentRef"
    class="bg-secondary min-h-[800px] max-w-screen-md w-full border rounded my-12 p-4 shadow-[0_0_10px_rgba(0,0,0,0.1)]"
>
```

Then after the closing `</div>` of that form card (line 268), add:

```html
<div
    v-if="editFormStore.formData && editFormStore.isSuccessActive"
    class="max-w-screen-md w-full my-12 px-4"
>
    <div class="flex flex-col gap-6 max-w-lg mx-auto">
        <h3 class="text-lg font-medium text-gray-900">Success Page</h3>
        <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-gray-700">Title</label>
            <input
                type="text"
                class="w-full rounded-md border border-gray-300 px-3 py-2 text-base focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
                placeholder="Thank you!"
                v-model="editFormStore.formData.success_title"
            />
        </div>
        <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-gray-700">Description</label>
            <TextEditor
                variant="outline"
                :content="editFormStore.formData.success_description"
                @change="(value: string) => (editFormStore.formData.success_description = value)"
                editor-class="bg-white w-full rounded-b border rounded-b min-h-40"
                placeholder="Write a message for the success page"
                :fixed-menu="true"
                :starterkit-options="{
                    heading: {
                        levels: [2, 3, 4, 5, 6],
                    },
                }"
            />
        </div>
    </div>
</div>
```

- [ ] **Step 5: Update the onCellChange handler to use activeSectionFields**

In `onCellChange` (line 48), change `editFormStore.fields` to `editFormStore.activeSectionFields`:

```typescript
const cells: FormField[] = editFormStore.activeSectionFields
    .filter(
        (f: FormField) =>
            (f.row_index ?? 0) === rowIndex && (f.column_index ?? 0) === colIndex
    )
    .sort((a: FormField, b: FormField) => (a.cell_index ?? 0) - (b.cell_index ?? 0));
```

- [ ] **Step 6: Run typecheck**

Run: `cd frontend && yarn typecheck`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add frontend/src/layouts/FormBuilderLayout.vue frontend/src/components/FormBuilderContent.vue
git commit -m "feat: wire SectionBar into layout and make canvas section-aware"
```

---

### Task 4: Remove Success Page editor from SettingsSection sidebar

**Files:**
- Modify: `frontend/src/components/builder/sidebar/SettingsSection.vue`

The success editor now lives in the canvas (Task 3), so remove it from the sidebar.

- [ ] **Step 1: Remove the Success Page section from SettingsSection**

Remove everything from line 103 to line 176 (the `<h5>Success Page</h5>` heading through the closing `</div>` of the success section, including the Dialog and expand button).

Also remove the unused imports. The `Dialog` and `TextEditor` imports (line 2) can be simplified to:

```typescript
import { Checkbox, FormControl, Tooltip } from "frappe-ui";
```

Remove `ref` from the `ref, watch` import if `inExpandedDescription` was the only ref (it was not, `showValidateMsg` and `routeExists` remain). The `ref` import stays.

Remove the `inExpandedDescription` ref (line 33):
```typescript
// DELETE: const inExpandedDescription = ref(false);
```

Also remove the `CircleCheck` import only if it's unused elsewhere. Check: `CircleCheck` is used for the route validation display (line 70). Keep it.

The remaining template should end after the "Allow Incomplete Forms" checkbox section (line 101).

- [ ] **Step 2: Run typecheck**

Run: `cd frontend && yarn typecheck`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/builder/sidebar/SettingsSection.vue
git commit -m "refactor: move success page editor from sidebar to canvas"
```

---

### Task 5: Manual verification

**Files:** None (testing only)

- [ ] **Step 1: Start the dev server**

Run: `cd frontend && npm run dev`

- [ ] **Step 2: Open the form builder in a browser**

Navigate to `http://localhost:8001/forms/edit-form/<any-form-id>`.

- [ ] **Step 3: Verify section bar appears**

Confirm:
- Section bar visible between header and canvas
- "Section 1" tab is active by default
- "+" button is present
- "Success" tab is pinned to the right

- [ ] **Step 4: Test adding a section**

Click "+". Confirm:
- "Section 2" tab appears
- Canvas switches to Section 2 (empty)
- Clicking "Section 1" shows original fields
- Clicking "Section 2" shows empty section

- [ ] **Step 5: Test adding fields to a section**

With Section 2 active, add a field from the sidebar. Confirm:
- Field appears in Section 2 canvas
- Switching to Section 1 does not show the new field
- Switching back to Section 2 shows it

- [ ] **Step 6: Test success tab**

Click "Success". Confirm:
- Form card disappears
- Success title input and description editor appear
- Changes to success title/description mark the form as unsaved
- Switching back to a section shows the form card again

- [ ] **Step 7: Test save**

Save the form (Cmd+S or Save button). Confirm:
- Form saves successfully
- Reload the page: sections persist (Page Break fields are saved)
- Section names persist

- [ ] **Step 8: Verify success editor removed from sidebar**

Open Settings tab in left sidebar. Confirm:
- "Success Page" section no longer appears in sidebar settings
