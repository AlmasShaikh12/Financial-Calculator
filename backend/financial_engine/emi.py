"""
Quarterly Instalment & Monthly EMI Calculator

PRIMARY: Quarterly Instalment
    Calculates illustrative quarterly instalment using the standard
    reducing-balance formula with quarterly periods:

        Q = P × R × (1 + R)^N / ((1 + R)^N - 1)

    Where:
        P = Loan principal
        R = Quarterly interest rate (annual rate / 4)
        N = Number of repayment quarterly instalments

    IMPORTANT: The moratorium is included within the stated repayment
    tenure. Instalments begin after the moratorium period. Therefore:

        N = (tenure_years × 4) − (moratorium_months / 3)

    Example — Term Loan:
        Tenure = 7 years = 28 quarters
        Moratorium = 6 months = 2 quarters
        Repayment instalments = 28 − 2 = 26 quarters

    Example — Micro Finance:
        Tenure = 3 years = 12 quarters
        Moratorium = 3 months = 1 quarter
        Repayment instalments = 12 − 1 = 11 quarters

SECONDARY: Monthly EMI (optional reference only)
    Calculates monthly EMI using the same formula with monthly periods.
    This is kept only as an optional "Monthly equivalent" for reference.
    It is NOT presented as the scheme's actual repayment amount.

IMPORTANT DISCLAIMER:
These are illustrative calculations based on the published beneficiary
interest rate. Actual repayment is subject to the sanctioned loan terms.
Interest during the moratorium period is NOT modelled here because the
official guidelines do not specify whether it is capitalised, waived, or
collected separately.
"""

from dataclasses import dataclass
from .schemes import FinancingScheme


@dataclass(frozen=True)
class QuarterlyInstalmentResult:
    """Result of a quarterly instalment calculation.

    All monetary values are in Indian Rupees (₹).

    Attributes:
        loan_amount: The loan principal used for calculation.
        annual_interest_rate: Annual interest rate (e.g., 0.08 for 8%).
        quarterly_interest_rate: Quarterly rate (annual / 4).
        tenure_years: Loan tenure in years.
        total_scheme_quarters: Total quarters in the scheme period.
        moratorium_quarters: Moratorium period in quarters.
        repayment_quarters: Number of repayment instalments (after moratorium).
        moratorium_months: Standard moratorium period in months.
        extended_moratorium_months: Extended moratorium for plantation/construction.
        quarterly_instalment: Calculated quarterly instalment amount.
        total_repayment: Total amount repaid over the repayment period.
        total_interest: Total interest paid over the repayment period.
        principal_amount: Original loan principal.
        repayment_frequency: "quarterly"
    """

    loan_amount: float
    annual_interest_rate: float
    quarterly_interest_rate: float
    tenure_years: int
    total_scheme_quarters: int
    moratorium_quarters: int
    repayment_quarters: int
    moratorium_months: int
    extended_moratorium_months: int
    quarterly_instalment: float
    total_repayment: float
    total_interest: float
    principal_amount: float
    repayment_frequency: str


@dataclass(frozen=True)
class MonthlyEMIResult:
    """Result of a monthly EMI calculation (optional reference only).

    This is NOT the scheme's actual repayment. It is provided only as a
    "Monthly equivalent" for users who find monthly figures easier to
    understand.
    """

    loan_amount: float
    annual_interest_rate: float
    monthly_interest_rate: float
    tenure_years: int
    total_months: int
    moratorium_months: int
    monthly_emi: float
    total_repayment: float
    total_interest: float


def calculate_quarterly_instalment(
    loan_amount: float, scheme: FinancingScheme
) -> QuarterlyInstalmentResult:
    """Calculate the illustrative quarterly instalment for a given loan and scheme.

    Uses the standard reducing-balance formula with quarterly periods:
        Q = P × R × (1 + R)^N / ((1 + R)^N - 1)

    The moratorium is included within the stated tenure. Instalments begin
    after the moratorium. Therefore:

        N = (tenure_years × 4) − (moratorium_months / 3)

    No interest is capitalised during the moratorium because the official
    guidelines do not specify how interest during moratorium is treated.

    Args:
        loan_amount: The loan principal in ₹.
        scheme: The applicable FinancingScheme with rate and tenure info.

    Returns:
        QuarterlyInstalmentResult with all calculated values.

    Raises:
        ValueError: If loan_amount is not positive.
    """
    if loan_amount <= 0:
        raise ValueError("Loan amount must be positive for instalment calculation.")

    P = loan_amount
    annual_rate = scheme.interest_rate_annual
    R = annual_rate / 4  # Quarterly interest rate

    # Total quarters in the scheme period
    total_scheme_quarters = scheme.tenure_years * 4

    # Moratorium in quarters (e.g., 6 months = 2 quarters)
    moratorium_quarters = scheme.moratorium_months // 3

    # Repayment quarters = total scheme quarters − moratorium quarters
    N = total_scheme_quarters - moratorium_quarters

    # Standard reducing-balance formula
    if R == 0:
        quarterly_instalment = P / N
    else:
        factor = (1 + R) ** N
        quarterly_instalment = P * R * factor / (factor - 1)

    total_repayment_raw = quarterly_instalment * N
    total_interest_raw = total_repayment_raw - P

    # Round after all calculations for consistency
    qi_rounded = round(quarterly_instalment, 2)
    total_rep_rounded = round(total_repayment_raw, 2)
    total_int_rounded = round(total_interest_raw, 2)

    return QuarterlyInstalmentResult(
        loan_amount=P,
        annual_interest_rate=annual_rate,
        quarterly_interest_rate=R,
        tenure_years=scheme.tenure_years,
        total_scheme_quarters=total_scheme_quarters,
        moratorium_quarters=moratorium_quarters,
        repayment_quarters=N,
        moratorium_months=scheme.moratorium_months,
        extended_moratorium_months=scheme.extended_moratorium_months,
        quarterly_instalment=qi_rounded,
        total_repayment=total_rep_rounded,
        total_interest=total_int_rounded,
        principal_amount=P,
        repayment_frequency=scheme.repayment_frequency,
    )


def calculate_monthly_emi_reference(
    loan_amount: float, scheme: FinancingScheme
) -> MonthlyEMIResult:
    """Calculate monthly EMI as an optional reference (NOT the scheme repayment).

    This function is kept for users who find monthly figures easier to
    understand. It is NOT presented as the scheme's actual repayment amount.

    Uses the standard reducing-balance formula with monthly periods:
        EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)

    Args:
        loan_amount: The loan principal in ₹.
        scheme: The applicable FinancingScheme.

    Returns:
        MonthlyEMIResult with the calculated monthly equivalent.

    Raises:
        ValueError: If loan_amount is not positive.
    """
    if loan_amount <= 0:
        raise ValueError("Loan amount must be positive for EMI calculation.")

    P = loan_amount
    annual_rate = scheme.interest_rate_annual
    r = annual_rate / 12  # Monthly interest rate

    # Monthly reference uses repayment months (excluding moratorium)
    total_scheme_months = scheme.tenure_years * 12
    n = total_scheme_months - scheme.moratorium_months  # Repayment months

    if r == 0:
        monthly_emi = P / n
    else:
        factor = (1 + r) ** n
        monthly_emi = P * r * factor / (factor - 1)

    total_repayment = round(monthly_emi * n, 2)
    total_interest = round(total_repayment - P, 2)

    return MonthlyEMIResult(
        loan_amount=P,
        annual_interest_rate=annual_rate,
        monthly_interest_rate=r,
        tenure_years=scheme.tenure_years,
        total_months=n,
        moratorium_months=scheme.moratorium_months,
        monthly_emi=round(monthly_emi, 2),
        total_repayment=total_repayment,
        total_interest=total_interest,
    )


def calculate_emi(loan_amount: float, scheme: FinancingScheme) -> MonthlyEMIResult:
    """Backward-compatible alias for the monthly EMI calculation."""
    return calculate_monthly_emi_reference(loan_amount, scheme)
