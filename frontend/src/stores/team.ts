import { defineStore } from "pinia";
import { useUser } from "./user";
import { computed, watch } from "vue";
import { useCall } from "frappe-ui";

export type TeamMember = {
  full_name: string;
  user_image: string | null;
  email: string;
};

export const useTeam = defineStore("team", () => {
  const user = useUser();
  const currentTeam = computed(() => user.currentTeam);
  const teamMembers = computed<TeamMember[]>(() => {
    const data = teamMembersResource.data;
    return Array.isArray(data) ? data : [];
  });

  const teamMembersResource = useCall({
    baseUrl: "/api/v2/method/",
    url: "forms_pro.api.team.get_team_members",
    params() {
      return {
        team_id: currentTeam.value?.name,
      };
    },
  });

  function initialize() {
    teamMembersResource.fetch();
  }

  watch(currentTeam, () => {
    teamMembersResource.fetch();
  });

  return {
    currentTeam,
    teamMembers,
    teamMembersResource,
    initialize,
  };
});
