"""
Repayment Schedule Generator

PRIMARY: Quarterly Repayment Schedule
    Generates a quarterly repayment schedule covering the FULL scheme tenure.
    The first N quarters are marked as "Moratorium" (no payments calculated),
    and the remaining quarters are marked as "Repayment" with instalment details.

    The moratorium is included within the stated tenure. Instalments
    begin after the moratorium period. No interest is capitalised
    during the moratorium because the treatment is unspecified.

SECONDARY: Monthly Repayment Schedule
    Generates a monthly breakdown for reference only, aggregated into
    quarterly summaries.

IMPORTANT ASSUMPTIONS:
- Quarterly instalment (principal + interest) is constant each quarter
  (standard annuity) during the repayment period.
- Interest is calculated on the remaining balance at the start of each
  repayment quarter using the quarterly rate (annual / 4).
- The moratorium period is displayed as explicit rows in the schedule.
  Interest during moratorium is NOT modelled because the official
  guidelines do not specify whether it is capitalised, waived,
  or collected separately.
- No prepayment, foreclosure, or processing fees are modelled.
"""

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Literal
from .schemes import FinancingScheme
from .emi import (
    calculate_quarterly_instalment,
    calculate_monthly_emi_reference,
    QuarterlyInstalmentResult,
    MonthlyEMIResult,
)


# ---------------------------------------------------------------------------
# Quarterly Schedule (PRIMARY)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QuarterlyPaymentEntry:
    """A single quarterly entry in the full scheme schedule.

    Attributes:
        quarter: Absolute quarter number within the scheme (1-indexed).
        status: "moratorium" or "repayment".
        repayment_number: Repayment instalment number (1-indexed) or None.
        opening_balance: Remaining balance at start of this quarter.
        instalment: Total quarterly instalment paid (0 for moratorium).
        principal_component: Portion of instalment that reduces principal (0 for moratorium).
        interest_component: Portion of instalment that is interest (None for moratorium).
        closing_balance: Remaining balance after this quarter.
    """

    quarter: int
    status: Literal["moratorium", "repayment"]
    repayment_number: int | None
    opening_balance: float
    instalment: float
    principal_component: float
    interest_component: float | None
    closing_balance: float


# ---------------------------------------------------------------------------
# Monthly Schedule (SECONDARY — for reference / quarterly aggregation)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MonthlyPaymentEntry:
    """A single monthly payment entry (reference only).

    Used for the optional monthly breakdown and for aggregating into
    quarterly summaries.
    """

    month: int
    opening_balance: float
    payment: float
    principal_component: float
    interest_component: float
    closing_balance: float


@dataclass(frozen=True)
class QuarterlyAggregate:
    """Aggregated quarterly summary from monthly data.

    Attributes:
        quarter: Quarter number (1-indexed).
        start_month: First month of this quarter.
        end_month: Last month of this quarter.
        principal_paid: Total principal paid in this quarter.
        interest_paid: Total interest paid in this quarter.
        total_payment: Total payment in this quarter.
        remaining_loan: Remaining loan balance at end of this quarter.
    """

    quarter: int
    start_month: int
    end_month: int
    principal_paid: float
    interest_paid: float
    total_payment: float
    remaining_loan: float


# ---------------------------------------------------------------------------
# Quarterly Schedule Generator (PRIMARY) — includes moratorium rows
# ---------------------------------------------------------------------------

def generate_quarterly_schedule(
    loan_amount: float,
    scheme: FinancingScheme,
) -> list[QuarterlyPaymentEntry]:
    """Generate the full quarterly schedule covering the entire scheme tenure.

    The schedule has total_scheme_quarters rows. The first moratorium_quarters
    rows are marked "moratorium" with no payment calculations. The remaining
    rows are marked "repayment" and use the standard reducing-balance
    amortisation approach.

    For moratorium rows:
        - instalment, principal_component = 0.0
        - interest_component = None (not calculated; treatment unspecified)
        - closing_balance = opening_balance (no reduction)

    For repayment rows:
        - Interest is charged on the current outstanding balance.
        - The remainder of the fixed quarterly instalment goes toward principal.

    Args:
        loan_amount: The loan principal in ₹.
        scheme: The applicable FinancingScheme.

    Returns:
        List of QuarterlyPaymentEntry objects covering the full tenure.

    Raises:
        ValueError: If loan_amount is not positive.
    """
    if loan_amount <= 0:
        raise ValueError("Loan amount must be positive.")

    qi_result = calculate_quarterly_instalment(loan_amount, scheme)
    instalment = qi_result.quarterly_instalment
    R = qi_result.quarterly_interest_rate
    N = qi_result.repayment_quarters  # Excludes moratorium
    total_quarters = qi_result.total_scheme_quarters
    moratorium_quarters = qi_result.moratorium_quarters

    schedule: list[QuarterlyPaymentEntry] = []
    balance = loan_amount

    for q in range(1, total_quarters + 1):
        if q <= moratorium_quarters:
            # --- Moratorium quarter ---
            schedule.append(
                QuarterlyPaymentEntry(
                    quarter=q,
                    status="moratorium",
                    repayment_number=None,
                    opening_balance=round(balance, 2),
                    instalment=0.0,
                    principal_component=0.0,
                    interest_component=None,  # Not calculated during moratorium
                    closing_balance=round(balance, 2),  # No change
                )
            )
        else:
            # --- Repayment quarter ---
            repayment_number = q - moratorium_quarters
            interest = round(balance * R, 2)
            principal = round(instalment - interest, 2)

            # Last instalment clears any rounding difference
            if repayment_number == N:
                principal = round(balance, 2)
                interest = round(balance * R, 2)
                actual_instalment = round(principal + interest, 2)
            else:
                actual_instalment = instalment

            new_balance = round(balance - principal, 2)
            if new_balance < 0:
                new_balance = 0.0

            schedule.append(
                QuarterlyPaymentEntry(
                    quarter=q,
                    status="repayment",
                    repayment_number=repayment_number,
                    opening_balance=round(balance, 2),
                    instalment=actual_instalment,
                    principal_component=principal,
                    interest_component=interest,
                    closing_balance=new_balance,
                )
            )
            balance = new_balance

    return schedule


# ---------------------------------------------------------------------------
# Monthly Schedule Generator (SECONDARY — reference only)
# ---------------------------------------------------------------------------

def generate_monthly_schedule(
    loan_amount: float,
    scheme: FinancingScheme,
) -> list[MonthlyPaymentEntry]:
    """Generate an optional monthly repayment breakdown (reference only).

    This is NOT the scheme's actual repayment schedule. It is provided
    only for users who prefer monthly granularity. The number of months
    excludes the moratorium.

    Args:
        loan_amount: The loan principal in ₹.
        scheme: The applicable FinancingScheme.

    Returns:
        List of MonthlyPaymentEntry objects.

    Raises:
        ValueError: If loan_amount is not positive.
    """
    if loan_amount <= 0:
        raise ValueError("Loan amount must be positive.")

    emi_result = calculate_monthly_emi_reference(loan_amount, scheme)
    monthly_emi = emi_result.monthly_emi
    r = emi_result.monthly_interest_rate
    n = emi_result.total_months  # Excludes moratorium

    schedule: list[MonthlyPaymentEntry] = []
    balance = loan_amount

    for month in range(1, n + 1):
        interest = round(balance * r, 2)
        principal = round(monthly_emi - interest, 2)

        if month == n:
            principal = round(balance, 2)
            interest = round(balance * r, 2)
            actual_payment = round(principal + interest, 2)
        else:
            actual_payment = monthly_emi

        new_balance = round(balance - principal, 2)
        if new_balance < 0:
            new_balance = 0.0

        schedule.append(
            MonthlyPaymentEntry(
                month=month,
                opening_balance=round(balance, 2),
                payment=actual_payment,
                principal_component=principal,
                interest_component=interest,
                closing_balance=new_balance,
            )
        )
        balance = new_balance

    return schedule


# ---------------------------------------------------------------------------
# Aggregate monthly data into quarterly summaries
# ---------------------------------------------------------------------------

def aggregate_monthly_to_quarterly(
    monthly_schedule: list[MonthlyPaymentEntry],
) -> list[QuarterlyAggregate]:
    """Aggregate a monthly repayment schedule into quarterly summaries.

    Each quarter covers 3 months. The last quarter may have fewer months
    if the total tenure is not a multiple of 3.

    Args:
        monthly_schedule: Monthly schedule from generate_monthly_schedule().

    Returns:
        List of QuarterlyAggregate objects.
    """
    if not monthly_schedule:
        return []

    quarterly: list[QuarterlyAggregate] = []
    quarter_num = 1

    for i in range(0, len(monthly_schedule), 3):
        chunk = monthly_schedule[i : i + 3]
        start_month = chunk[0].month
        end_month = chunk[-1].month

        principal_paid = round(sum(e.principal_component for e in chunk), 2)
        interest_paid = round(sum(e.interest_component for e in chunk), 2)
        total_payment = round(sum(e.payment for e in chunk), 2)
        remaining_loan = chunk[-1].closing_balance

        quarterly.append(
            QuarterlyAggregate(
                quarter=quarter_num,
                start_month=start_month,
                end_month=end_month,
                principal_paid=principal_paid,
                interest_paid=interest_paid,
                total_payment=total_payment,
                remaining_loan=remaining_loan,
            )
        )
        quarter_num += 1

    return quarterly


def generate_repayment_schedule(
    loan_amount: float,
    scheme: FinancingScheme,
) -> list[SimpleNamespace]:
    """Backward-compatible monthly repayment entries expected by the API."""
    monthly = generate_monthly_schedule(loan_amount, scheme)
    return [
        SimpleNamespace(
            month=item.month,
            opening_balance=item.opening_balance,
            emi_amount=item.payment,
            principal_component=item.principal_component,
            interest_component=item.interest_component,
            closing_balance=item.closing_balance,
        )
        for item in monthly
    ]


def generate_quarterly_summary(
    schedule: list[SimpleNamespace],
) -> list[SimpleNamespace]:
    """Aggregate a repayment schedule into quarter-level summaries."""
    if not schedule:
        return []

    quarterly: list[SimpleNamespace] = []
    for index in range(0, len(schedule), 3):
        chunk = schedule[index : index + 3]
        quarterly.append(
            SimpleNamespace(
                quarter=(index // 3) + 1,
                start_month=chunk[0].month,
                end_month=chunk[-1].month,
                principal_paid=round(sum(item.principal_component for item in chunk), 2),
                interest_paid=round(sum(item.interest_component for item in chunk), 2),
                total_payment=round(sum(item.emi_amount for item in chunk), 2),
                remaining_loan=chunk[-1].closing_balance,
            )
        )
    return quarterly
