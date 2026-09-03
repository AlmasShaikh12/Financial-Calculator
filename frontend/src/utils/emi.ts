/**
 * Quarterly Instalment & Monthly EMI Calculator (TypeScript)
 *
 * PRIMARY: Quarterly Instalment
 *   Q = P × R × (1+R)^N / ((1+R)^N - 1)
 *   R = annual rate / 4
 *   N = (tenure_years × 4) − (moratorium_months / 3)
 *
 *   The moratorium is included within the stated tenure. Instalments
 *   begin after the moratorium. No interest is capitalised during
 *   the moratorium because the treatment is unspecified.
 *
 * SECONDARY: Monthly EMI (reference only, NOT the scheme repayment)
 *
 * IMPORTANT: These are illustrative calculations based on the published
 * beneficiary interest rate. Actual repayment is subject to the sanctioned
 * loan terms.
 */

import { FinancingScheme } from "./schemes";

export interface QuarterlyInstalmentResult {
  loanAmount: number;
  annualInterestRate: number;
  quarterlyInterestRate: number;
  tenureYears: number;
  totalSchemeQuarters: number;
  moratoriumQuarters: number;
  repaymentQuarters: number;
  moratoriumMonths: number;
  extendedMoratoriumMonths: number;
  quarterlyInstalment: number;
  totalRepayment: number;
  totalInterest: number;
  principalAmount: number;
  repaymentFrequency: string;
}

export interface MonthlyEMIResult {
  loanAmount: number;
  annualInterestRate: number;
  monthlyInterestRate: number;
  tenureYears: number;
  totalMonths: number;
  monthlyEmi: number;
  totalRepayment: number;
  totalInterest: number;
}

/**
 * Calculate illustrative quarterly instalment (PRIMARY repayment).
 * Moratorium is included in the tenure; instalments start after.
 */
export function calculateQuarterlyInstalment(
  loanAmount: number,
  scheme: FinancingScheme
): QuarterlyInstalmentResult {
  if (loanAmount <= 0) {
    throw new Error("Loan amount must be positive.");
  }

  const P = loanAmount;
  const annualRate = scheme.interestRateAnnual;
  const R = annualRate / 4;

  // Total quarters in the scheme period
  const totalSchemeQuarters = scheme.tenureYears * 4;

  // Moratorium in quarters
  const moratoriumQuarters = Math.floor(scheme.moratoriumMonths / 3);

  // Repayment quarters = total scheme quarters − moratorium quarters
  const N = totalSchemeQuarters - moratoriumQuarters;

  let qi: number;
  if (R === 0) {
    qi = P / N;
  } else {
    const factor = Math.pow(1 + R, N);
    qi = (P * R * factor) / (factor - 1);
  }

  const totalRepayment = qi * N;
  const totalInterest = totalRepayment - P;

  return {
    loanAmount: P,
    annualInterestRate: annualRate,
    quarterlyInterestRate: R,
    tenureYears: scheme.tenureYears,
    totalSchemeQuarters,
    moratoriumQuarters,
    repaymentQuarters: N,
    moratoriumMonths: scheme.moratoriumMonths,
    extendedMoratoriumMonths: scheme.extendedMoratoriumMonths,
    quarterlyInstalment: Math.round(qi * 100) / 100,
    totalRepayment: Math.round(totalRepayment * 100) / 100,
    totalInterest: Math.round(totalInterest * 100) / 100,
    principalAmount: P,
    repaymentFrequency: scheme.repaymentFrequency,
  };
}

/**
 * Calculate monthly EMI as optional reference (NOT the scheme repayment).
 * Moratorium months are excluded from the repayment period.
 */
export function calculateMonthlyEmiReference(
  loanAmount: number,
  scheme: FinancingScheme
): MonthlyEMIResult {
  if (loanAmount <= 0) {
    throw new Error("Loan amount must be positive.");
  }

  const P = loanAmount;
  const r = scheme.interestRateAnnual / 12;

  // Repayment months exclude moratorium
  const totalSchemeMonths = scheme.tenureYears * 12;
  const n = totalSchemeMonths - scheme.moratoriumMonths;

  let emi: number;
  if (r === 0) {
    emi = P / n;
  } else {
    const factor = Math.pow(1 + r, n);
    emi = (P * r * factor) / (factor - 1);
  }

  const totalRepayment = emi * n;
  const totalInterest = totalRepayment - P;

  return {
    loanAmount: P,
    annualInterestRate: scheme.interestRateAnnual,
    monthlyInterestRate: r,
    tenureYears: scheme.tenureYears,
    totalMonths: n,
    monthlyEmi: Math.round(emi * 100) / 100,
    totalRepayment: Math.round(totalRepayment * 100) / 100,
    totalInterest: Math.round(totalInterest * 100) / 100,
  };
}
