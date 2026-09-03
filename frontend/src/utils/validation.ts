/**
 * Input Validation (TypeScript)
 *
 * Mirrors the Python financial_engine.validation module.
 */

import {
  MAX_SUPPORTED_PROJECT_COST,
  MAX_SUPPORTED_LOAN_AMOUNT,
} from "./schemes";

export interface ValidationResult {
  isValid: boolean;
  value: number | null;
  errorMessage: string | null;
}

/**
 * Validate the user's margin capital input.
 */
export function validateMargin(rawInput: string): ValidationResult {
  if (rawInput === null || rawInput === undefined) {
    return {
      isValid: false,
      value: null,
      errorMessage: "Please enter your available margin capital.",
    };
  }

  const stripped = rawInput.trim();
  if (!stripped) {
    return {
      isValid: false,
      value: null,
      errorMessage: "Please enter your available margin capital.",
    };
  }

  // Remove currency symbols and commas
  const cleaned = stripped.replace(/[₹,\s]/g, "");
  const value = parseFloat(cleaned);

  if (isNaN(value)) {
    return {
      isValid: false,
      value: null,
      errorMessage: "Please enter a valid number (e.g., 100000).",
    };
  }

  if (value === 0) {
    return {
      isValid: false,
      value: 0,
      errorMessage: "Margin capital must be greater than zero.",
    };
  }

  if (value < 0) {
    return {
      isValid: false,
      value,
      errorMessage: "Margin capital cannot be negative.",
    };
  }

  return { isValid: true, value, errorMessage: null };
}

export interface SchemeLimitResult {
  withinLimits: boolean;
  exceedsLimit: boolean;
  maxProjectCost: number;
  maxLoanAmount: number;
  warningMessage: string | null;
}

/**
 * Check if the calculated project cost is within scheme limits.
 */
export function checkSchemeLimits(
  projectCost: number
): SchemeLimitResult {
  if (projectCost <= MAX_SUPPORTED_PROJECT_COST) {
    return {
      withinLimits: true,
      exceedsLimit: false,
      maxProjectCost: MAX_SUPPORTED_PROJECT_COST,
      maxLoanAmount: MAX_SUPPORTED_LOAN_AMOUNT,
      warningMessage: null,
    };
  }

  return {
    withinLimits: false,
    exceedsLimit: true,
    maxProjectCost: MAX_SUPPORTED_PROJECT_COST,
    maxLoanAmount: MAX_SUPPORTED_LOAN_AMOUNT,
    warningMessage: `Your calculated project cost exceeds the maximum project cost supported by the schemes in this prototype. Maximum supported project cost: ₹${MAX_SUPPORTED_PROJECT_COST.toLocaleString("en-IN")}. Maximum stated loan amount: ₹${MAX_SUPPORTED_LOAN_AMOUNT.toLocaleString("en-IN")}.`,
  };
}
