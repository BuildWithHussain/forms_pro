import { computed, type Ref } from "vue";
import type { FormField } from "@/types/formfield";

export function useGroupedRows(fields: Ref<FormField[]>) {
  return computed<FormField[][]>(() => {
    const rows = new Map<number, FormField[]>();
    for (const f of fields.value) {
      const r = f.row_index ?? 0;
      if (!rows.has(r)) rows.set(r, []);
      rows.get(r)!.push(f);
    }
    return [...rows.keys()]
      .sort((a, b) => a - b)
      .map((r) =>
        rows
          .get(r)!
          .slice()
          .sort((a, b) => (a.column_index ?? 0) - (b.column_index ?? 0))
      );
  });
}
