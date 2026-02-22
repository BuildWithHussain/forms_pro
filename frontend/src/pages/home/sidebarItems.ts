import { Files, UsersRound } from "lucide-vue-next";
import { computed } from "vue";
import { useRoute } from "vue-router";
import type { SidebarProps } from "frappe-ui";

type SidebarSectionProps = NonNullable<
  SidebarProps["sections"]
> extends (infer T)[]
  ? T
  : never;

export function useSidebarItems() {
  const route = useRoute();
  const isActive = (path: string) => route.path === path;

  return computed((): SidebarSectionProps[] => [
    {
      items: [
        {
          label: "All Forms",
          to: "/",
          icon: Files,
          isActive: isActive("/"),
        },
      ],
    },
    {
      items: [
        {
          label: "Team",
          to: "/team",
          icon: UsersRound,
          isActive: isActive("/team"),
        },
      ],
    },
  ]);
}
