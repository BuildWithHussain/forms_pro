import { computed } from "vue";
import { useRouteData as useStore } from "@/stores/routeData";

export function useRouteData<T = unknown>() {
  const store = useStore();
  return {
    status: computed(() => store.state.status),
    data: computed(() => store.state.data as T | undefined),
    error: computed(() => store.state.error),
    isNavigating: computed(() => store.isNavigating),
  };
}
