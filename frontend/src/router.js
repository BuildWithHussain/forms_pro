import { userResource } from "@/data/user";
import { createRouter, createWebHistory } from "vue-router";
import { session } from "./data/session";

const routes = [
    {
        path: "/",
        name: "Dashboard",
        component: () => import("@/pages/Dashboard.vue"),
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
        path: "/p/:route",
        name: "Form Submission Page",
        component: () => import("@/pages/SubmissionPage.vue"),
    },
];

const router = createRouter({
    history: createWebHistory("/forms"),
    routes,
});

router.beforeEach(async (to, from, next) => {
    let isLoggedIn = session.isLoggedIn;
    try {
        await userResource.promise;
    } catch (error) {
        isLoggedIn = false;
    }

    if (to.name === "Login" && isLoggedIn) {
        next({ name: "Home" });
    } else if (to.name !== "Login" && !isLoggedIn) {
        window.location.href = `/login?redirect-to=/forms${to.fullPath}`;
    } else {
        next();
    }
});

export default router;
