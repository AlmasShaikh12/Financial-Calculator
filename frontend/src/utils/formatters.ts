/**
 * Formatting Utilities
 *
 * Indian number formatting (₹1,00,000) using Intl.NumberFormat.
 */

/**
 * Format a number as Indian currency: ₹1,00,000
 *
 * @param amount - The amount to format
 * @param showSymbol - Whether to prefix with ₹ (default: true)
 */
export function formatINR(amount: number, showSymbol = true): string {
  const formatted = new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
  }).format(Math.round(amount));

  return showSymbol ? `₹${formatted}` : formatted;
}

/**
 * Format a number as Indian currency with decimals: ₹1,00,000.50
 */
export function formatINRDecimal(amount: number): string {
  const formatted = new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
  }).format(amount);

  return `₹${formatted}`;
}

/**
 * Format percentage: 8% or 6.5%
 */
export function formatPercent(rate: number): string {
  const percent = rate * 100;
  // Avoid floating point display issues
  return `${parseFloat(percent.toPrecision(4))}%`;
}

/**
 * Format years with label: "7 years" or "3 years"
 */
export function formatTenure(years: number): string {
  return `${years} year${years !== 1 ? "s" : ""}`;
}

/**
 * Format months with label: "6 months" or "3 months"
 */
export function formatMonths(months: number): string {
  return `${months} month${months !== 1 ? "s" : ""}`;
}

/**
 * Format quarters with label: "28 quarters" or "12 quarters"
 */
export function formatQuarters(quarters: number): string {
  return `${quarters} quarter${quarters !== 1 ? "s" : ""}`;
}
