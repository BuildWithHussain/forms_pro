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
            path: "/categories",
            name: "Categories",
            component: () => import("@/pages/Categories.vue"),
        },
        {
            path: "/submissions",
            name: "Submissions",
            component: () => import("@/pages/Submissions.vue"),
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
    // Catch-all route - redirect unknown routes to dashboard
    {
        path: "/:pathMatch(.*)*",
        name: "NotFound",
        redirect: { name: "Dashboard" },
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

        // Handle authentication - only protect dashboard, categories, submissions, and edit form routes
        // Submission pages should be accessible to guests
        const protectedRoutes = ["Dashboard", "Categories", "Submissions", "Edit Form"];
    const isProtectedRoute = protectedRoutes.includes(to.name || "");
    
    if (to.name === "Login" && isLoggedIn) {
        next({ name: "Dashboard" });
    } else if (isProtectedRoute && !isLoggedIn) {
        // Redirect to login with return path
        const returnPath = to.fullPath.startsWith("/") ? to.fullPath : `/${to.fullPath}`;
        window.location.href = `/login?redirect-to=/forms${returnPath}`;
    } else {
        next();
    }
});

export default router;
