import {
  ConditionalLogic,
  ConditionalOperators,
  Condition,
  Actions,
} from "@/types/conditional-render.types";
import { FormField } from "@/types/formfield";

/**
 * Parse conditional_logic string into ConditionalLogic object
 */
export function parseConditionalLogic(
  conditionalLogic: string | undefined | null
): ConditionalLogic | null {
  if (!conditionalLogic || conditionalLogic.trim() === "") {
    return null;
  }

  try {
    return JSON.parse(conditionalLogic) as ConditionalLogic;
  } catch (e) {
    console.error("Failed to parse conditional_logic:", e);
    return null;
  }
}

/**
 * Get the value of a field from form data, handling different field types
 */
function getFieldValue(
  fieldValue: any,
  fieldType: string
): string | number | boolean | null {
  if (fieldValue === null || fieldValue === undefined || fieldValue === "") {
    return null;
  }

  // Handle boolean/switch fields
  if (fieldType === "Switch" || fieldType === "Checkbox") {
    return Boolean(fieldValue);
  }

  // Handle number fields
  if (fieldType === "Number") {
    const num = Number(fieldValue);
    return isNaN(num) ? null : num;
  }

  // Handle string fields
  return String(fieldValue);
}

/**
 * Normalize values for comparison (convert to strings for most comparisons)
 */
function normalizeValue(value: any): string | number | boolean | null {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value === "boolean") {
    return value;
  }
  if (typeof value === "number") {
    return value;
  }
  return String(value).trim();
}

/**
 * Evaluate a single condition against form field values
 */
function evaluateCondition(
  condition: Condition,
  formValues: Record<string, any>,
  allFields: FormField[]
): boolean {
  const { fieldname, operator, value } = condition;

  // Get the field definition to understand its type
  const field = allFields.find((f) => f.fieldname === fieldname);
  if (!field) {
    console.warn(`Field ${fieldname} not found in form fields`);
    return false;
  }

  const fieldValue = getFieldValue(formValues[fieldname], field.fieldtype);
  const conditionValue = normalizeValue(value);
  const normalizedFieldValue = normalizeValue(fieldValue);

  switch (operator) {
    case ConditionalOperators.Is:
      return normalizedFieldValue === conditionValue;

    case ConditionalOperators.IsNot:
      return normalizedFieldValue !== conditionValue;

    case ConditionalOperators.IsEmpty:
      return (
        normalizedFieldValue === null ||
        normalizedFieldValue === "" ||
        normalizedFieldValue === undefined
      );

    case ConditionalOperators.IsNotEmpty:
      return (
        normalizedFieldValue !== null &&
        normalizedFieldValue !== "" &&
        normalizedFieldValue !== undefined
      );

    case ConditionalOperators.IsSet:
      return (
        normalizedFieldValue !== null && normalizedFieldValue !== undefined
      );

    case ConditionalOperators.Contains:
      if (normalizedFieldValue === null) return false;
      return String(normalizedFieldValue)
        .toLowerCase()
        .includes(String(conditionValue).toLowerCase());

    case ConditionalOperators.DoesNotContain:
      if (normalizedFieldValue === null) return true;
      return !String(normalizedFieldValue)
        .toLowerCase()
        .includes(String(conditionValue).toLowerCase());

    case ConditionalOperators.IsLessThan:
      if (
        typeof normalizedFieldValue === "number" &&
        typeof conditionValue === "number"
      ) {
        return normalizedFieldValue < conditionValue;
      }
      return false;

    case ConditionalOperators.IsLessThanOrEqualTo:
      if (
        typeof normalizedFieldValue === "number" &&
        typeof conditionValue === "number"
      ) {
        return normalizedFieldValue <= conditionValue;
      }
      return false;

    case ConditionalOperators.IsGreaterThan:
      if (
        typeof normalizedFieldValue === "number" &&
        typeof conditionValue === "number"
      ) {
        return normalizedFieldValue > conditionValue;
      }
      return false;

    case ConditionalOperators.IsGreaterThanOrEqualTo:
      if (
        typeof normalizedFieldValue === "number" &&
        typeof conditionValue === "number"
      ) {
        return normalizedFieldValue >= conditionValue;
      }
      return false;

    case ConditionalOperators.StartsWith:
      if (normalizedFieldValue === null) return false;
      return String(normalizedFieldValue)
        .toLowerCase()
        .startsWith(String(conditionValue).toLowerCase());

    case ConditionalOperators.DoesNotStartWith:
      if (normalizedFieldValue === null) return true;
      return !String(normalizedFieldValue)
        .toLowerCase()
        .startsWith(String(conditionValue).toLowerCase());

    case ConditionalOperators.EndsWith:
      if (normalizedFieldValue === null) return false;
      return String(normalizedFieldValue)
        .toLowerCase()
        .endsWith(String(conditionValue).toLowerCase());

    case ConditionalOperators.DoesNotEndWith:
      if (normalizedFieldValue === null) return true;
      return !String(normalizedFieldValue)
        .toLowerCase()
        .endsWith(String(conditionValue).toLowerCase());

    default:
      console.warn(`Unknown operator: ${operator}`);
      return false;
  }
}

/**
 * Evaluate all conditions in a ConditionalLogic object
 * Currently supports AND logic (all conditions must be true)
 * TODO: Add support for OR logic if needed
 */
function evaluateConditions(
  conditionalLogic: ConditionalLogic,
  formValues: Record<string, any>,
  allFields: FormField[]
): boolean {
  if (
    !conditionalLogic.conditions ||
    conditionalLogic.conditions.length === 0
  ) {
    return false;
  }

  // All conditions must be true (AND logic)
  return conditionalLogic.conditions.every((condition) =>
    evaluateCondition(condition, formValues, allFields)
  );
}

/**
 * Determine if a field should be visible based on conditional logic rules
 * defined on other fields that target this field. Visibility is driven by
 * rules on other fields, not a property on the field itself. A field is visible if:
 * - No conditional logic rules target it, OR
 * - At least one "Show Field" action evaluates to true, OR
 * - No "Hide Field" actions evaluate to true
 */
export function shouldFieldBeVisible(
  field: FormField,
  formValues: Record<string, any>,
  allFields: FormField[]
): boolean {
  // Find all conditional logic rules that target this field
  const targetingRules: ConditionalLogic[] = [];

  allFields.forEach((otherField) => {
    if (!otherField.conditional_logic) return;

    const logic = parseConditionalLogic(otherField.conditional_logic);
    if (logic && logic.target_field === field.fieldname) {
      targetingRules.push(logic);
    }
  });

  // If no rules target this field, it's visible
  if (targetingRules.length === 0) {
    return true;
  }

  // Check each rule
  let hasShowRule = false;
  let hasHideRule = false;

  for (const rule of targetingRules) {
    const conditionsMet = evaluateConditions(rule, formValues, allFields);

    if (conditionsMet) {
      if (rule.action === Actions.ShowField) {
        hasShowRule = true;
      } else if (rule.action === Actions.HideField) {
        hasHideRule = true;
      }
    }
  }

  // If any "Show Field" rule is met, field is visible
  if (hasShowRule) {
    return true;
  }

  // If any "Hide Field" rule is met, field is hidden
  if (hasHideRule) {
    return false;
  }

  // Default: field is visible if no rules are met
  return true;
}

/**
 * Determine if a field should be required based on conditional logic
 */
export function shouldFieldBeRequired(
  field: FormField,
  formValues: Record<string, any>,
  allFields: FormField[]
): boolean {
  // Start with the field's base required status
  let isRequired = field.reqd || false;

  // Find all conditional logic rules that target this field with "Require Answer"
  const targetingRules: ConditionalLogic[] = [];

  allFields.forEach((otherField) => {
    if (!otherField.conditional_logic) return;

    const logic = parseConditionalLogic(otherField.conditional_logic);
    if (
      logic &&
      logic.target_field === field.fieldname &&
      logic.action === Actions.RequireAnswer
    ) {
      targetingRules.push(logic);
    }
  });

  // If any "Require Answer" rule conditions are met, make field required
  for (const rule of targetingRules) {
    if (evaluateConditions(rule, formValues, allFields)) {
      isRequired = true;
      break;
    }
  }

  return isRequired;
}

/**
 * Get all fields that should be visible based on current form values
 */
export function getVisibleFields(
  fields: FormField[],
  formValues: Record<string, any>
): FormField[] {
  return fields.filter((field) =>
    shouldFieldBeVisible(field, formValues, fields)
  );
}
