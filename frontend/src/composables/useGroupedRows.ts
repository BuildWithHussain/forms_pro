import { computed, type Ref } from "vue";
import type { FormField } from "@/types/formfield";

export function useGroupedRows(fields: Ref<FormField[]>) {
  return computed<FormField[][][]>(() => {
    const rows = new Map<number, Map<number, FormField[]>>();
    for (const f of fields.value) {
      const r = f.row_index ?? 0;
      const c = f.column_index ?? 0;
      if (!rows.has(r)) rows.set(r, new Map());
      const cols = rows.get(r)!;
      if (!cols.has(c)) cols.set(c, []);
      cols.get(c)!.push(f);
    }
    return [...rows.keys()]
      .sort((a, b) => a - b)
      .map((r) => {
        const cols = rows.get(r)!;
        return [...cols.keys()]
          .sort((a, b) => a - b)
          .map((c) =>
            cols
              .get(c)!
              .slice()
              .sort((a, b) => (a.cell_index ?? 0) - (b.cell_index ?? 0))
          );
      });
  });
}
