import type { ThemePreferenceType } from "@/utils/theme";
import setTheme from "@/utils/theme";
import { createResource } from "frappe-ui";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

type UserTeam = {
  name: string;
  team_name: string;
  is_current: boolean;
};

export const useUser = defineStore("user", () => {
  const user = computed(() => userResource.data);
  const userTeams = computed<UserTeam[]>(() => userTeamsResource.data);
  const currentTeam = ref<UserTeam | null>(null);

  const userResource = createResource({
    url: "forms_pro.api.user.get_user",
  });

  const userTeamsResource = createResource({
    url: "forms_pro.api.user.get_user_teams",
  });

  async function initialize() {
    await Promise.all([userResource.fetch(), userTeamsResource.fetch()]);
    const _currTeam = getCurrentTeamFromAllTeams();
    if (_currTeam) {
      setCurrentTeam(_currTeam);
    }
  }

  function fetchUser() {
    userResource.fetch();
  }

  function fetchUserTeams() {
    userTeamsResource.fetch();
  }

  function getCurrentTeamFromAllTeams() {
    return userTeams.value?.find((team) => team.is_current);
  }

  function setCurrentTeam(team: UserTeam) {
    currentTeam.value = team;
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
    toggleThemePreference,
  };
});
