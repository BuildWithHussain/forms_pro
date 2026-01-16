<script setup lang="ts">
import { computed, ref, watch, onMounted } from "vue";
import { FormControl } from "frappe-ui";
import { ChevronDown, ChevronUp } from "lucide-vue-next";
import { onClickOutside } from "@vueuse/core";

export type Country = {
    code: string; // ISO country code (e.g., "IN", "US")
    dialCode: string; // Phone dial code (e.g., "+91", "+1")
    name: string; // Country name (e.g., "India", "United States")
    flag: string; // Flag emoji (e.g., "🇮🇳", "🇺🇸")
};

const props = defineProps({
    field: {
        type: Object,
        required: true,
    },
    countries: {
        type: Array as () => Country[],
        default: () => [],
    },
    variant: {
        type: String as () => "outline" | "subtle" | undefined,
        default: "outline" as const,
    },
});

const emit = defineEmits(["update:modelValue", "change"]);

const modelValue = defineModel<string>();

// Default country list (comprehensive list of countries with dial codes)
const defaultCountries: Country[] = [
    { code: "IN", dialCode: "+91", name: "India", flag: "🇮🇳" },
    { code: "US", dialCode: "+1", name: "United States", flag: "🇺🇸" },
    { code: "GB", dialCode: "+44", name: "United Kingdom", flag: "🇬🇧" },
    { code: "CA", dialCode: "+1", name: "Canada", flag: "🇨🇦" },
    { code: "AU", dialCode: "+61", name: "Australia", flag: "🇦🇺" },
    { code: "DE", dialCode: "+49", name: "Germany", flag: "🇩🇪" },
    { code: "FR", dialCode: "+33", name: "France", flag: "🇫🇷" },
    { code: "IT", dialCode: "+39", name: "Italy", flag: "🇮🇹" },
    { code: "ES", dialCode: "+34", name: "Spain", flag: "🇪🇸" },
    { code: "NL", dialCode: "+31", name: "Netherlands", flag: "🇳🇱" },
    { code: "BE", dialCode: "+32", name: "Belgium", flag: "🇧🇪" },
    { code: "CH", dialCode: "+41", name: "Switzerland", flag: "🇨🇭" },
    { code: "AT", dialCode: "+43", name: "Austria", flag: "🇦🇹" },
    { code: "SE", dialCode: "+46", name: "Sweden", flag: "🇸🇪" },
    { code: "NO", dialCode: "+47", name: "Norway", flag: "🇳🇴" },
    { code: "DK", dialCode: "+45", name: "Denmark", flag: "🇩🇰" },
    { code: "FI", dialCode: "+358", name: "Finland", flag: "🇫🇮" },
    { code: "PL", dialCode: "+48", name: "Poland", flag: "🇵🇱" },
    { code: "PT", dialCode: "+351", name: "Portugal", flag: "🇵🇹" },
    { code: "GR", dialCode: "+30", name: "Greece", flag: "🇬🇷" },
    { code: "IE", dialCode: "+353", name: "Ireland", flag: "🇮🇪" },
    { code: "NZ", dialCode: "+64", name: "New Zealand", flag: "🇳🇿" },
    { code: "JP", dialCode: "+81", name: "Japan", flag: "🇯🇵" },
    { code: "CN", dialCode: "+86", name: "China", flag: "🇨🇳" },
    { code: "KR", dialCode: "+82", name: "South Korea", flag: "🇰🇷" },
    { code: "SG", dialCode: "+65", name: "Singapore", flag: "🇸🇬" },
    { code: "MY", dialCode: "+60", name: "Malaysia", flag: "🇲🇾" },
    { code: "TH", dialCode: "+66", name: "Thailand", flag: "🇹🇭" },
    { code: "ID", dialCode: "+62", name: "Indonesia", flag: "🇮🇩" },
    { code: "PH", dialCode: "+63", name: "Philippines", flag: "🇵🇭" },
    { code: "VN", dialCode: "+84", name: "Vietnam", flag: "🇻🇳" },
    { code: "BD", dialCode: "+880", name: "Bangladesh", flag: "🇧🇩" },
    { code: "PK", dialCode: "+92", name: "Pakistan", flag: "🇵🇰" },
    { code: "LK", dialCode: "+94", name: "Sri Lanka", flag: "🇱🇰" },
    { code: "AE", dialCode: "+971", name: "United Arab Emirates", flag: "🇦🇪" },
    { code: "SA", dialCode: "+966", name: "Saudi Arabia", flag: "🇸🇦" },
    { code: "IL", dialCode: "+972", name: "Israel", flag: "🇮🇱" },
    { code: "TR", dialCode: "+90", name: "Turkey", flag: "🇹🇷" },
    { code: "RU", dialCode: "+7", name: "Russia", flag: "🇷🇺" },
    { code: "BR", dialCode: "+55", name: "Brazil", flag: "🇧🇷" },
    { code: "MX", dialCode: "+52", name: "Mexico", flag: "🇲🇽" },
    { code: "AR", dialCode: "+54", name: "Argentina", flag: "🇦🇷" },
    { code: "CL", dialCode: "+56", name: "Chile", flag: "🇨🇱" },
    { code: "CO", dialCode: "+57", name: "Colombia", flag: "🇨🇴" },
    { code: "PE", dialCode: "+51", name: "Peru", flag: "🇵🇪" },
    { code: "ZA", dialCode: "+27", name: "South Africa", flag: "🇿🇦" },
    { code: "EG", dialCode: "+20", name: "Egypt", flag: "🇪🇬" },
    { code: "NG", dialCode: "+234", name: "Nigeria", flag: "🇳🇬" },
    { code: "KE", dialCode: "+254", name: "Kenya", flag: "🇰🇪" },
];

// Use provided countries or default to all countries
const availableCountries = computed(() => {
    return props.countries.length > 0 ? props.countries : defaultCountries;
});

// Convert countries to Select options format
const countryOptions = computed(() => {
    return availableCountries.value.map((country) => ({
        label: `${country.flag} ${country.dialCode} ${country.name}`,
        value: country.code,
        country: country, // Store full country object for easy access
    }));
});

// Default to India if available, otherwise first country
const getDefaultCountryCode = (): string => {
    const india = availableCountries.value.find((c) => c.code === "IN");
    return india ? "IN" : availableCountries.value[0]?.code || "";
};

const selectedCountryCode = ref<string>(getDefaultCountryCode());
const phoneNumber = ref<string>("");
const isCountryDropdownOpen = ref(false);
const countryDropdownRef = ref<HTMLElement | null>(null);
const countryButtonRef = ref<HTMLElement | null>(null);

// Close dropdown when clicking outside
onClickOutside(
    countryButtonRef,
    () => {
        isCountryDropdownOpen.value = false;
    },
    { ignore: [countryDropdownRef] }
);

// Get selected country object
const selectedCountry = computed(() => {
    return (
        availableCountries.value.find((c) => c.code === selectedCountryCode.value) ||
        availableCountries.value[0]
    );
});

// Get full phone number with country code (for display - with space)
const getFullPhoneNumber = (): string => {
    if (!phoneNumber.value) return "";
    return `${selectedCountry.value.dialCode} ${phoneNumber.value}`.trim();
};

// Sanitize phone number: convert space to dash and remove dashes from number part (for model storage)
const sanitizePhoneNumber = (phoneNumber: string): string => {
    if (!phoneNumber) return "";
    // Match country code and number parts (handles both space and dash separators)
    const match = phoneNumber.match(/^(\+\d+)[\s-]+(.+)$/);
    if (match) {
        const countryCode = match[1];
        const numberPart = match[2].replace(/-/g, ""); // Remove all dashes from number part
        // Return as "+91-1234567890" (dash between country code and number, no dashes in number)
        return `${countryCode}-${numberPart}`;
    }
    // Fallback: if format doesn't match, return as-is (shouldn't happen in normal flow)
    return phoneNumber;
};

// Watch for changes and update model value
const updatePhoneValue = () => {
    const fullNumber = getFullPhoneNumber();
    // Sanitize: convert space to dash before emitting to model
    const sanitizedNumber = sanitizePhoneNumber(fullNumber);
    emit("update:modelValue", sanitizedNumber);
    emit("change", sanitizedNumber);
};

// Parse phone number from modelValue
const parsePhoneNumber = (value: string) => {
    if (!value) {
        phoneNumber.value = "";
        return;
    }

    // Convert dash to space for display (model has "+91-1234567890", display as "+91 1234567890")
    const displayValue = value.replace(/^(\+\d+)-/, "$1 ");

    // If value starts with +, try to find matching country
    if (displayValue.startsWith("+")) {
        // Find country by matching dial code (longest match first)
        const sortedCountries = [...availableCountries.value].sort(
            (a, b) => b.dialCode.length - a.dialCode.length
        );
        const country = sortedCountries.find((c) => displayValue.startsWith(c.dialCode));

        if (country) {
            selectedCountryCode.value = country.code;
            phoneNumber.value = displayValue.replace(country.dialCode, "").trim();
        } else {
            phoneNumber.value = displayValue;
        }
    } else {
        phoneNumber.value = displayValue;
    }
};

// Initialize from modelValue if provided
onMounted(() => {
    if (modelValue.value) {
        parsePhoneNumber(modelValue.value);
    }
});

// Watch for external modelValue changes
watch(
    () => modelValue.value,
    (newValue) => {
        if (newValue !== getFullPhoneNumber()) {
            parsePhoneNumber(newValue || "");
        }
    }
);

// Watch country code changes
const handleCountryChange = (countryCode: string) => {
    selectedCountryCode.value = countryCode;
    updatePhoneValue();
};

// Watch phone number changes
const handlePhoneNumberChange = (value: string) => {
    phoneNumber.value = value;
    updatePhoneValue();
};
</script>

<template>
    <div class="flex flex-col gap-2">
        <div class="relative">
            <FormControl
                :model-value="phoneNumber"
                @update:model-value="handlePhoneNumberChange"
                type="tel"
                :placeholder="field.placeholder || 'Example: 081234 56789'"
                :variant="variant as 'outline' | 'subtle' | undefined"
                :description="field.description"
                :disabled="field.disabled"
                :readonly="field.readonly"
                class="phone-input-with-prefix"
            >
                <template #prefix>
                    <div class="relative flex items-center h-full">
                        <button
                            ref="countryButtonRef"
                            type="button"
                            @click.stop="isCountryDropdownOpen = !isCountryDropdownOpen"
                            class="flex items-center gap-1 px-2 h-full hover:bg-gray-100 focus:outline-none focus:bg-gray-100 whitespace-nowrap border-r border-gray-300 pr-2 mr-2 min-w-[85px]"
                        >
                            <span class="text-base leading-none flex-shrink-0">{{
                                selectedCountry?.flag
                            }}</span>
                            <span
                                class="text-sm font-medium text-gray-700 leading-none flex-shrink-0"
                                >{{ selectedCountry?.dialCode }}</span
                            >
                            <div class="flex flex-col ml-auto flex-shrink-0">
                                <ChevronUp class="w-3 h-3 text-gray-500" />
                                <ChevronDown class="w-3 h-3 text-gray-500 -mt-1" />
                            </div>
                        </button>

                        <!-- Dropdown Menu -->
                        <div
                            v-if="isCountryDropdownOpen"
                            ref="countryDropdownRef"
                            class="absolute top-full left-0 mt-1 w-64 max-h-60 overflow-y-auto bg-white border border-gray-300 rounded-md shadow-lg z-50"
                            @click.stop
                        >
                            <div class="p-1">
                                <div
                                    v-for="option in countryOptions"
                                    :key="option.value"
                                    @click="
                                        handleCountryChange(option.value);
                                        isCountryDropdownOpen = false;
                                    "
                                    class="flex items-center gap-2 px-3 py-2 cursor-pointer hover:bg-gray-100 rounded"
                                    :class="{
                                        'bg-blue-50': selectedCountryCode === option.value,
                                    }"
                                >
                                    <span class="text-lg">{{ option.country.flag }}</span>
                                    <span class="text-sm font-medium text-gray-700">{{
                                        option.country.dialCode
                                    }}</span>
                                    <span class="text-sm text-gray-600 ml-auto">{{
                                        option.country.name
                                    }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </FormControl>
        </div>
    </div>
</template>

<style scoped>
/* Adjust input padding to account for wider prefix */
:deep(.phone-input-with-prefix input) {
    padding-left: 6.5rem !important; /* Account for prefix width (~85px + padding) */
}
</style>
