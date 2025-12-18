import type { ThemePreferenceType } from "@/utils/theme";
import setTheme from "@/utils/theme";
import { createResource } from "frappe-ui";
import { defineStore } from "pinia";
import { computed } from "vue";

export const useUser = defineStore("user", () => {
  const user = computed(() => userResource.data);
  const userTeams = computed(() => userTeamsResource.data);

  const userResource = createResource({
    url: "forms_pro.api.user.get_user",
  });

  const userTeamsResource = createResource({
    url: "forms_pro.api.user.get_user_teams",
  });

  async function initialize() {
    await Promise.all([userResource.fetch(), userTeamsResource.fetch()]);
  }

  function fetchUser() {
    userResource.fetch();
  }

  function fetchUserTeams() {
    userTeamsResource.fetch();
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
      userResource.value?.reload();
    });
  }

  return {
    user,
    userTeams,
    initialize,
    fetchUser,
    fetchUserTeams,
    toggleThemePreference,
  };
});
