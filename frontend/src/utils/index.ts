/**
 * Financial Engine — TypeScript barrel export.
 *
 * Mirrors the Python financial_engine package for future React integration.
 * Re-export all public types and functions.
 */

export {
  type FinancingScheme,
  MICRO_FINANCE_SCHEME,
  TERM_LOAN_SCHEME,
  SCHEMES,
  MAX_SUPPORTED_PROJECT_COST,
  MAX_SUPPORTED_LOAN_AMOUNT,
  selectScheme,
} from "./schemes";

export {
  CONTRIBUTION_PERCENTAGE,
  FUNDING_PERCENTAGE,
  calculateProjectCost,
  calculateLoanAmount,
  calculateMarginFromProjectCost,
} from "./calculations";

export {
  type QuarterlyInstalmentResult,
  type MonthlyEMIResult,
  calculateQuarterlyInstalment,
  calculateMonthlyEmiReference,
} from "./emi";

export {
  type QuarterlyPaymentEntry,
  type MonthlyPaymentEntry,
  type QuarterlyAggregate,
  generateQuarterlySchedule,
  generateMonthlySchedule,
  aggregateMonthlyToQuarterly,
} from "./repayment";

export {
  type ValidationResult,
  type SchemeLimitResult,
  validateMargin,
  checkSchemeLimits,
} from "./validation";

export {
  formatINR,
  formatINRDecimal,
  formatPercent,
  formatTenure,
  formatMonths,
} from "./formatters";
