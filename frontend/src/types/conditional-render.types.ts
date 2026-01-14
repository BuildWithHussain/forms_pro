export enum ConditionalOperators {
  Is = "Is",
  IsNot = "Is Not",
  IsEmpty = "Is Empty",
  IsNotEmpty = "Is Not Empty",
  IsSet = "Is Set",
  Contains = "Contains",
  DoesNotContain = "Does Not Contain",
  IsLessThan = "Is Less Than",
  IsLessThanOrEqualTo = "Is Less Than Or Equal To",
  IsGreaterThan = "Is Greater Than",
  IsGreaterThanOrEqualTo = "Is Greater Than Or Equal To",
  StartsWith = "Starts With",
  DoesNotStartWith = "Does Not Start With",
  EndsWith = "Ends With",
  DoesNotEndWith = "Does Not End With",
}

export enum LogicOperators {
  And = "And",
  Or = "Or",
}

export type Condition = {
  fieldname: string;
  operator: ConditionalOperators;
  value: string | number | boolean;
};

export enum Actions {
  ShowField = "Show Field",
  HideField = "Hide Field",
  RequireAnswer = "Require Answer",
}

export type ConditionalLogic = {
  conditions: Condition[];
  action: Actions;
  target_field: string | null;
};
