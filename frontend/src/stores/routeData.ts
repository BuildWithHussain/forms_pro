import { defineStore } from "pinia";
import { ref } from "vue";
import type { RouteLocationNormalized } from "vue-router";

type Status = "idle" | "loading" | "ok" | "error";

interface RouteError {
  excType?: string;
  httpStatus?: number;
  messages: string[];
}

interface RouteState {
  status: Status;
  data: unknown;
  error: RouteError | null;
}

export const useRouteData = defineStore("routeData", () => {
  const state = ref<RouteState>({ status: "idle", data: null, error: null });
  const isNavigating = ref(false);

  async function resolve(route: RouteLocationNormalized): Promise<void> {
    const fetchFn = route.meta.fetch;
    state.value = { status: "loading", data: null, error: null };
    isNavigating.value = true;

    try {
      if (!fetchFn) {
        state.value = { status: "ok", data: null, error: null };
        return;
      }
      const resource = fetchFn(route);
      const data = await resource.fetch();
      state.value = { status: "ok", data, error: null };
    } catch (err: any) {
      state.value = {
        status: "error",
        data: null,
        error: {
          excType: err?.exc_type,
          httpStatus: err?.response?.status,
          messages: err?.messages?.length
            ? err.messages
            : [err?.message ?? "Something went wrong"],
        },
      };
    } finally {
      isNavigating.value = false;
    }
  }

  function clear(): void {
    state.value = { status: "idle", data: null, error: null };
  }

  return { state, isNavigating, resolve, clear };
});
