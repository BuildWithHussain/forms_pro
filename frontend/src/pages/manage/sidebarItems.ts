import { ArrowLeft, LayoutGrid, ListChecks } from "@lucide/vue";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { SidebarProps } from "frappe-ui";

type SidebarSectionProps = NonNullable<
  SidebarProps["sections"]
> extends (infer T)[]
  ? T
  : never;

export function useManageFormSidebarItems() {
  const route = useRoute();
  const router = useRouter();
  const formId = computed(() => route.params.id as string);

  return computed((): SidebarSectionProps[] => [
    {
      items: [
        {
          label: "Go Back",
          icon: ArrowLeft,
          onClick: () => router.replace("/"),
        },
      ],
    },
    {
      label: "",
      items: [
        {
          label: "Overview",
          to: `/manage/${formId.value}/overview`,
          icon: LayoutGrid,
          isActive: route.name === "Manage Form Overview",
        },
        {
          label: "Submissions",
          to: `/manage/${formId.value}/submissions`,
          icon: ListChecks,
          isActive: route.name === "Manage Form Submissions",
        },
      ],
    },
  ]);
}
