/**
 * Repayment Schedule Generator (TypeScript)
 *
 * Mirrors the Python financial_engine.repayment module.
 * PRIMARY: Quarterly repayment schedule (full tenure with moratorium rows)
 * SECONDARY: Monthly repayment breakdown (reference only)
 *
 * The schedule covers the FULL scheme tenure. Moratorium quarters are
 * displayed as explicit rows with status "moratorium". Repayment quarters
 * follow after the moratorium period.
 */

import { FinancingScheme } from "./schemes";
import {
  calculateQuarterlyInstalment,
  calculateMonthlyEmiReference,
  QuarterlyInstalmentResult,
  MonthlyEMIResult,
} from "./emi";

// Quarterly Schedule Entry (PRIMARY) — includes moratorium rows
export interface QuarterlyPaymentEntry {
  quarter: number;               // Absolute quarter (1-indexed)
  status: "moratorium" | "repayment";
  repaymentNumber: number | null; // Repayment instalment number or null
  openingBalance: number;
  instalment: number;
  principalComponent: number;
  interestComponent: number | null; // null during moratorium
  closingBalance: number;
}

// Monthly Schedule Entry (SECONDARY — reference only)
export interface MonthlyPaymentEntry {
  month: number;
  openingBalance: number;
  payment: number;
  principalComponent: number;
  interestComponent: number;
  closingBalance: number;
}

// Aggregated quarterly summary from monthly data
export interface QuarterlyAggregate {
  quarter: number;
  startMonth: number;
  endMonth: number;
  principalPaid: number;
  interestPaid: number;
  totalPayment: number;
  remainingLoan: number;
}

/**
 * Generate the primary quarterly repayment schedule.
 * Covers the FULL scheme tenure including moratorium rows.
 *
 * - First moratoriumQuarters rows: status "moratorium", no payments
 * - Remaining rows: status "repayment", standard reducing-balance amortisation
 */
export function generateQuarterlySchedule(
  loanAmount: number,
  scheme: FinancingScheme
): QuarterlyPaymentEntry[] {
  if (loanAmount <= 0) {
    throw new Error("Loan amount must be positive.");
  }

  const qiResult = calculateQuarterlyInstalment(loanAmount, scheme);
  const instalment = qiResult.quarterlyInstalment;
  const R = qiResult.quarterlyInterestRate;
  const N = qiResult.repaymentQuarters; // Excludes moratorium
  const totalQuarters = qiResult.totalSchemeQuarters;
  const moratoriumQuarters = qiResult.moratoriumQuarters;

  const schedule: QuarterlyPaymentEntry[] = [];
  let balance = loanAmount;

  for (let q = 1; q <= totalQuarters; q++) {
    if (q <= moratoriumQuarters) {
      // --- Moratorium quarter ---
      schedule.push({
        quarter: q,
        status: "moratorium",
        repaymentNumber: null,
        openingBalance: Math.round(balance * 100) / 100,
        instalment: 0,
        principalComponent: 0,
        interestComponent: null, // Not calculated during moratorium
        closingBalance: Math.round(balance * 100) / 100, // No change
      });
    } else {
      // --- Repayment quarter ---
      const repaymentNumber = q - moratoriumQuarters;
      const interest = Math.round(balance * R * 100) / 100;
      let principal = Math.round((instalment - interest) * 100) / 100;
      let actualInstalment = instalment;

      if (repaymentNumber === N) {
        principal = Math.round(balance * 100) / 100;
        actualInstalment = Math.round((principal + interest) * 100) / 100;
      }

      let newBalance = Math.round((balance - principal) * 100) / 100;
      if (newBalance < 0) newBalance = 0;

      schedule.push({
        quarter: q,
        status: "repayment",
        repaymentNumber,
        openingBalance: Math.round(balance * 100) / 100,
        instalment: actualInstalment,
        principalComponent: principal,
        interestComponent: interest,
        closingBalance: newBalance,
      });

      balance = newBalance;
    }
  }

  return schedule;
}

/**
 * Generate optional monthly repayment breakdown (reference only).
 * Moratorium months are excluded.
 */
export function generateMonthlySchedule(
  loanAmount: number,
  scheme: FinancingScheme
): MonthlyPaymentEntry[] {
  if (loanAmount <= 0) {
    throw new Error("Loan amount must be positive.");
  }

  const emiResult = calculateMonthlyEmiReference(loanAmount, scheme);
  const monthlyEmi = emiResult.monthlyEmi;
  const r = emiResult.monthlyInterestRate;
  const n = emiResult.totalMonths; // Excludes moratorium

  const schedule: MonthlyPaymentEntry[] = [];
  let balance = loanAmount;

  for (let month = 1; month <= n; month++) {
    const interest = Math.round(balance * r * 100) / 100;
    let principal = Math.round((monthlyEmi - interest) * 100) / 100;
    let actualPayment = monthlyEmi;

    if (month === n) {
      principal = Math.round(balance * 100) / 100;
      interest = Math.round(balance * r * 100) / 100;
      actualPayment = Math.round((principal + interest) * 100) / 100;
    }

    let newBalance = Math.round((balance - principal) * 100) / 100;
    if (newBalance < 0) newBalance = 0;

    schedule.push({
      month,
      openingBalance: Math.round(balance * 100) / 100,
      payment: actualPayment,
      principalComponent: principal,
      interestComponent: interest,
      closingBalance: newBalance,
    });

    balance = newBalance;
  }

  return schedule;
}

/**
 * Aggregate monthly data into quarterly summaries.
 */
export function aggregateMonthlyToQuarterly(
  monthlySchedule: MonthlyPaymentEntry[]
): QuarterlyAggregate[] {
  if (monthlySchedule.length === 0) return [];

  const quarterly: QuarterlyAggregate[] = [];
  let quarterNum = 1;

  for (let i = 0; i < monthlySchedule.length; i += 3) {
    const chunk = monthlySchedule.slice(i, i + 3);
    const startMonth = chunk[0].month;
    const endMonth = chunk[chunk.length - 1].month;

    const principalPaid =
      Math.round(
        chunk.reduce((sum, e) => sum + e.principalComponent, 0) * 100
      ) / 100;
    const interestPaid =
      Math.round(
        chunk.reduce((sum, e) => sum + e.interestComponent, 0) * 100
      ) / 100;
    const totalPayment =
      Math.round(chunk.reduce((sum, e) => sum + e.payment, 0) * 100) / 100;
    const remainingLoan = chunk[chunk.length - 1].closingBalance;

    quarterly.push({
      quarter: quarterNum,
      startMonth,
      endMonth,
      principalPaid,
      interestPaid,
      totalPayment,
      remainingLoan,
    });
    quarterNum++;
  }

  return quarterly;
}
