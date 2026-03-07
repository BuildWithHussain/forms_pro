import { userResource } from "@/data/user";
import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import { session } from "./data/session";
import { isLoginRequired } from "@/utils/form";

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
      },
    ],
  },
  {
    path: "/manage/:id",
    name: "Manage Form",
    component: () => import("@/pages/manage/ManageForm.vue"),
    redirect: { name: "Manage Form Overview" },
    children: [
      {
        path: "overview",
        name: "Manage Form Overview",
        component: () => import("@/pages/manage/overview/Overview.vue"),
      },
    ],
  },
  {
    path: "/edit-form/:id",
    name: "Edit Form",
    component: () => import("@/pages/EditForm.vue"),
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

router.beforeEach(async (to, _from, next) => {
  let isLoggedIn = session.isLoggedIn;
  try {
    await userResource.promise;
  } catch (error) {
    isLoggedIn = false;
  }

  if (to.name === "Login" && isLoggedIn) {
    next({ name: "Home" });
  } else if (
    to.name !== "Login" &&
    !isLoggedIn &&
    to.meta.allowGuest !== true
  ) {
    window.location.href = `/login?redirect-to=/forms${to.fullPath}`;
  } else {
    next();
  }
});

export default router;
