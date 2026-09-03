/**
 * Core Financial Calculations (TypeScript)
 *
 * Deterministic functions for project cost, loan amount, and margin.
 * Mirrors the Python financial_engine.calculations module.
 *
 * Assumption: Beneficiary contributes 10% of project cost.
 */

import { FinancingScheme } from "./schemes";

export const CONTRIBUTION_PERCENTAGE = 0.1; // 10%
export const FUNDING_PERCENTAGE = 0.9; // 90%

/**
 * Project Cost = Available Margin Capital / 0.10
 */
export function calculateProjectCost(marginCapital: number): number {
  if (marginCapital <= 0) {
    throw new Error("Margin capital must be positive.");
  }
  return marginCapital / CONTRIBUTION_PERCENTAGE;
}

/**
 * Loan Amount = Project Cost × Funding Percentage (capped at scheme max).
 */
export function calculateLoanAmount(
  projectCost: number,
  scheme: FinancingScheme
): number {
  if (projectCost < 0) {
    throw new Error("Project cost cannot be negative.");
  }
  const calculated = projectCost * scheme.fundingPercentage;
  return Math.min(calculated, scheme.maxLoanAmount);
}

/**
 * Reverse: Margin = Project Cost × Contribution Percentage
 */
export function calculateMarginFromProjectCost(projectCost: number): number {
  if (projectCost < 0) {
    throw new Error("Project cost cannot be negative.");
  }
  return projectCost * CONTRIBUTION_PERCENTAGE;
}
