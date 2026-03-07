import { defineStore } from "pinia";
import { useUser } from "./user";
import { computed, watch } from "vue";
import { useCall, createResource } from "frappe-ui";
import { toast } from "vue-sonner";

export type TeamMember = {
  full_name: string;
  user_image: string | null;
  email: string;
  can_edit_team: boolean;
  is_owner: boolean;
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

  function toggleEditPermissionForMember(member_email: string) {
    createResource({
      url: "forms_pro.api.team.toggle_can_edit_team",
      method: "POST",
      makeParams() {
        return {
          team_id: currentTeam.value?.name,
          member_email: member_email,
        };
      },
      async onSuccess() {
        await teamMembersResource.fetch();
        toast.info("Edit Permission Updated");
      },
      onError(error: Error) {
        console.error(error);
        toast.error(`Failed to update edit permission`);
      },
    }).submit();
  }

  function removeMemberFromTeam(member_email: string) {
    createResource({
      url: "forms_pro.api.team.remove_member_from_team",
      method: "POST",
      makeParams() {
        return {
          team_id: currentTeam.value?.name,
          member_email: member_email,
        };
      },
      onSuccess() {
        teamMembersResource.reload();
        toast.success("Member removed from team");
      },
      onError(error: Error) {
        console.error(error);
        toast.error(`Failed to remove member from team`);
      },
    }).submit();
  }

  async function save(fields: { team_name?: string; logo?: string }) {
    createResource({
      url: "forms_pro.api.team.save",
      method: "POST",
      makeParams() {
        return {
          team_id: currentTeam.value?.name,
          fields,
        };
      },
      async onSuccess() {
        toast.success("Team Details Updated");
        await teamMembersResource.fetch();
        user.fetchUserTeams();
      },
      onError(error: Error) {
        console.error(error);
        toast.error("Failed to update team " + error.message);
      },
    }).submit();
  }

  watch(currentTeam, () => {
    teamMembersResource.fetch();
  });

  return {
    currentTeam,
    teamMembers,
    teamMembersResource,
    initialize,
    toggleEditPermissionForMember,
    removeMemberFromTeam,
    save,
  };
});
