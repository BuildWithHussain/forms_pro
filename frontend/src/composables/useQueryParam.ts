import { ref, watch, type Ref } from "vue";
import { useRoute, useRouter } from "vue-router";

/**
 * Composable for syncing a reactive value with a URL query parameter
 *
 * @param paramName - The name of the query parameter
 * @param defaultValue - Default value if param is not present or invalid
 * @param validValues - Optional array of valid values. If provided, only these values will be accepted
 * @param options - Optional configuration
 * @returns A reactive ref that stays in sync with the URL query parameter
 *
 * @example
 * ```ts
 * const selectedTab = useQueryParam('tab', 'description', ['description', 'shared']);
 * ```
 */
export function useQueryParam<T extends string>(
  paramName: string,
  defaultValue: T,
  validValues?: T[],
  options?: {
    /**
     * Whether to update the URL immediately if param is missing (default: true)
     */
    setInitialParam?: boolean;
    /**
     * Whether to use router.replace (true) or router.push (false) (default: true)
     */
    replace?: boolean;
  }
): Ref<T> {
  const route = useRoute();
  const router = useRouter();
  const { setInitialParam = true, replace = true } = options || {};

  // Get initial value from URL or use default
  const getInitialValue = (): T => {
    const paramValue = route.query[paramName];

    if (!paramValue || typeof paramValue !== "string") {
      return defaultValue;
    }

    // If valid values are provided, validate against them
    if (validValues && !validValues.includes(paramValue as T)) {
      return defaultValue;
    }

    return paramValue as T;
  };

  const value = ref<T>(getInitialValue()) as Ref<T>;

  // Update URL when value changes
  watch(value, (newValue) => {
    const currentParam = route.query[paramName];

    // Only update if the value actually changed
    if (currentParam !== newValue) {
      const updateMethod = replace ? router.replace : router.push;
      updateMethod({
        ...route,
        query: {
          ...route.query,
          [paramName]: newValue,
        },
      });
    }
  });

  // Update value when URL query param changes (e.g., browser back/forward)
  watch(
    () => route.query[paramName],
    (newParam) => {
      if (!newParam || typeof newParam !== "string") {
        // If param is removed, set to default
        if (value.value !== defaultValue) {
          value.value = defaultValue;
        }
        return;
      }

      // If valid values are provided, validate
      if (validValues && !validValues.includes(newParam as T)) {
        if (value.value !== defaultValue) {
          value.value = defaultValue;
        }
        return;
      }

      // Update value if it changed
      if (value.value !== newParam) {
        value.value = newParam as T;
      }
    }
  );

  // Set initial URL param if not present
  if (setInitialParam && !route.query[paramName]) {
    const updateMethod = replace ? router.replace : router.push;
    updateMethod({
      ...route,
      query: {
        ...route.query,
        [paramName]: value.value,
      },
    });
  }

  return value;
}
