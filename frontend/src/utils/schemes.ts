/**
 * Scheme Configuration — MoSJE Annual Report 2025-26
 *
 * Source: Ministry of Social Justice & Empowerment Annual Report 2025-26
 * (NSFDC concessional financing schemes)
 *
 * DISCLAIMER: These parameters are based on the SIH problem statement
 * and verified against the MoSJE Annual Report 2025-26. Actual eligibility,
 * sanction, and repayment terms are subject to the latest official
 * guidelines and the sanctioning agency.
 */

export interface FinancingScheme {
  name: string;
  description: string;
  maxProjectCost: number;
  fundingPercentage: number; // 0.0 to 1.0
  maxLoanAmount: number;
  interestRateAnnual: number; // decimal, e.g. 0.08 for 8%
  tenureYears: number;
  moratoriumMonths: number;
  extendedMoratoriumMonths: number; // For plantation/construction
  minProjectCost: number;
  repaymentFrequency: string; // "quarterly"
  sourceReference: string;
}

export const MICRO_FINANCE_SCHEME: FinancingScheme = {
  name: "Micro Finance Scheme",
  description:
    "Concessional micro-finance for projects up to ₹1.40 lakh. Funding agency provides up to 90% as a concessional loan. Repayment in quarterly instalments within 3 years.",
  maxProjectCost: 140000,
  fundingPercentage: 0.9,
  maxLoanAmount: 125000,
  interestRateAnnual: 0.065,
  tenureYears: 3,
  moratoriumMonths: 3,
  extendedMoratoriumMonths: 0,
  minProjectCost: 0,
  repaymentFrequency: "quarterly",
  sourceReference:
    "MoSJE Annual Report 2025-26 — NSFDC Micro Finance Scheme. Subject to verification against current official guidelines.",
};

export const TERM_LOAN_SCHEME: FinancingScheme = {
  name: "Term Loan Scheme",
  description:
    "Term loan for projects above ₹1.40 lakh and up to ₹50 lakh. Funding agency provides up to 90% as a concessional loan. Repayment in quarterly instalments within 7 years. Extended moratorium of 12 months for plantation and construction.",
  maxProjectCost: 5000000,
  fundingPercentage: 0.9,
  maxLoanAmount: 4500000,
  interestRateAnnual: 0.08,
  tenureYears: 7,
  moratoriumMonths: 6,
  extendedMoratoriumMonths: 12,
  minProjectCost: 140000,
  repaymentFrequency: "quarterly",
  sourceReference:
    "MoSJE Annual Report 2025-26 — NSFDC Term Loan Scheme. Subject to verification against current official guidelines.",
};

export const SCHEMES: FinancingScheme[] = [
  MICRO_FINANCE_SCHEME,
  TERM_LOAN_SCHEME,
];

export const MAX_SUPPORTED_PROJECT_COST = 5000000;
export const MAX_SUPPORTED_LOAN_AMOUNT = 4500000;

/**
 * Select the appropriate financing scheme based on project cost.
 *
 * - Project cost ≤ ₹1,40,000  → Micro Finance
 * - ₹1,40,000 < cost ≤ ₹50,00,000 → Term Loan
 * - cost > ₹50,00,000 → No scheme
 */
export function selectScheme(
  projectCost: number
): FinancingScheme | null {
  for (const scheme of SCHEMES) {
    if (projectCost <= scheme.maxProjectCost) {
      return scheme;
    }
  }
  return null;
}
