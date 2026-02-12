import type { ThemePreferenceType } from "@/utils/theme";
import setTheme from "@/utils/theme";
import { createResource } from "frappe-ui";
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { toast } from "vue-sonner";

export type UserTeam = {
  name: string;
  team_name: string;
  logo: string | null;
  is_current: boolean;
};

export const useUser = defineStore("user", () => {
  const user = computed(() => userResource.data);
  const userTeams = computed<UserTeam[]>(() => userTeamsResource.data);
  const currentTeam = ref<UserTeam | null>(null);

  const userResource = createResource({
    url: "forms_pro.api.user.get_current_user",
  });

  const userTeamsResource = createResource({
    url: "forms_pro.api.user.get_user_teams",
    onSuccess(data: UserTeam[]) {
      const _currTeam = data.find((team) => team.is_current);
      if (!_currTeam) {
        if (data.length > 0) {
          setCurrentTeam(data[0]);
        }
        return;
      }
      setCurrentTeam(_currTeam);
    },
    onError(error: Error) {
      toast.error("Failed to fetch user teams", {
        description: error.message,
      });
    },
  });

  async function initialize() {
    await userResource.fetch();
    await userTeamsResource.fetch();
  }

  function fetchUser() {
    userResource.fetch();
  }

  function fetchUserTeams() {
    userTeamsResource.fetch();
  }

  // @ts-ignore
  function getCurrentTeamFromAllTeams() {
    return userTeams.value?.find((team) => team.is_current);
  }

  function setCurrentTeam(team: UserTeam) {
    currentTeam.value = team;
  }

  function switchTeam(team: UserTeam) {
    createResource({
      url: "forms_pro.api.team.switch_team",
      method: "POST",
      makeParams() {
        return {
          team_id: team.name,
        };
      },
      onSuccess() {
        userTeamsResource.reload();
        toast.success("Team switched successfully");
      },
      onError(error: Error) {
        toast.error("Failed to switch team", {
          description: error.message,
        });
      },
    }).submit();
  }

  function createTeam(teamName: string, logoUrl: string | undefined) {
    createResource({
      url: "forms_pro.api.team.create_team",
      method: "POST",
      makeParams() {
        return {
          team_name: teamName,
          logo_url: logoUrl,
        };
      },
      onSuccess() {
        userTeamsResource.reload();
        toast.success("Team created successfully");
      },
      onError(error: Error) {
        toast.error("Failed to create team", {
          description: error.message,
        });
      },
    }).submit();
  }

  async function toggleThemePreference(theme: ThemePreferenceType) {
    setTheme(theme);

    const switchTheme = createResource({
      url: "frappe.core.doctype.user.user.switch_theme",
      params: {
        theme,
      },
    });
    await switchTheme.fetch().then(() => {
      userResource.reload();
    });
  }

  return {
    user,
    userTeams,
    currentTeam,
    initialize,
    fetchUser,
    fetchUserTeams,
    setCurrentTeam,
    createTeam,
    switchTeam,
    toggleThemePreference,
  };
});
