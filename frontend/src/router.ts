import { userResource } from "@/data/user";
import { session } from "@/data/session";
import { useRouteData } from "@/stores/routeData";
import { useUser } from "@/stores/user";
import { isLoginRequired } from "@/utils/form";
import { createResource } from "frappe-ui";
import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";

const formForViewResource = (id: string) =>
  createResource({
    url: "forms_pro.api.form.get_form_for_view",
    params: { form_id: id },
    cache: ["FormView", id],
    auto: false,
  });

const formForEditResource = (id: string) =>
  createResource({
    url: "forms_pro.api.form.get_form_for_edit",
    params: { form_id: id },
    cache: ["FormEdit", id],
    auto: false,
  });

const teamForManageResource = (teamId: string) =>
  createResource({
    url: "forms_pro.api.team.get_team_for_manage",
    params: { team_id: teamId },
    cache: ["TeamManage", teamId],
    auto: false,
  });

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/pages/home/Home.vue"),
    children: [
      {
        path: "",
        name: "Dashboard",
        component: () => import("@/pages/home/Dashboard.vue"),
      },
      {
        path: "team",
        name: "Manage Team",
        component: () => import("@/pages/team/ManageTeam.vue"),
        meta: {
          fetch: () => {
            const user = useUser();
            return teamForManageResource(user.currentTeam?.name ?? "");
          },
        },
      },
    ],
  },
  {
    path: "/manage/:id",
    name: "Manage Form",
    component: () => import("@/pages/manage/ManageForm.vue"),
    redirect: { name: "Manage Form Overview" },
    meta: {
      fetch: (route) => formForViewResource(route.params.id as string),
    },
    children: [
      {
        path: "overview",
        name: "Manage Form Overview",
        component: () => import("@/pages/manage/overview/Overview.vue"),
      },
      {
        path: "submissions",
        name: "Manage Form Submissions",
        component: () => import("@/pages/manage/submissions/Submissions.vue"),
      },
    ],
  },
  {
    path: "/edit-form/:id",
    name: "Edit Form",
    component: () => import("@/pages/EditForm.vue"),
    meta: {
      fetch: (route) => formForEditResource(route.params.id as string),
    },
  },
  {
    path: "/p/:route(.*)",
    name: "Form Submission Page",
    component: () => import("@/pages/SubmissionPage.vue"),
    meta: { allowGuest: true },
    beforeEnter: async (to, _from) => {
      const loginRequired = await isLoginRequired(to.params.route as string);

      if (loginRequired && !session.isLoggedIn) {
        window.location.href = `/login?redirect-to=/forms${to.fullPath}`;
        return false;
      }
      return true;
    },
  },
  {
    path: "/p/:route(.*)/edit/:submissionName",
    name: "Public Edit Submission Page",
    component: () => import("@/pages/submission/PublicEdit.vue"),
  },
];

const router = createRouter({
  history: createWebHistory("/forms"),
  routes,
});

router.beforeEach(async (to, _from) => {
  let isLoggedIn = session.isLoggedIn;
  try {
    await userResource.promise;
  } catch {
    isLoggedIn = false;
  }

  if (to.name === "Login" && isLoggedIn) return { name: "Home" };
  if (to.meta.allowGuest) return true;
  if (!isLoggedIn) {
    window.location.href = `/login?redirect-to=/forms${to.fullPath}`;
    return false;
  }

  const store = useRouteData();
  await store.resolve(to);
  return true;
});

export default router;
