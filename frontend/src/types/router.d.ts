import "vue-router";
import type { RouteLocationNormalized } from "vue-router";

declare module "vue-router" {
  interface RouteMeta {
    allowGuest?: boolean;
    fetch?: (route: RouteLocationNormalized) => {
      fetch: () => Promise<unknown>;
    };
  }
}

export {};
