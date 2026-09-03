"""
SIH Financial Engine - Reliable Financial Calculator & Scheme Router

This module provides deterministic financial calculations for the SIH
(Smart India Hackathon) financing model where the beneficiary contributes
approximately 10% of the project cost and the funding agency provides up
to 90% as a concessional loan.

Source: Ministry of Social Justice & Empowerment Annual Report 2025-26
(NSFDC concessional financing schemes)

IMPORTANT DISCLAIMER:
All scheme parameters and calculations are based on the SIH problem
statement and verified against the MoSJE Annual Report 2025-26. They are
for advisory/illustrative purposes only. Actual eligibility, sanction, and
repayment terms MUST be verified against the latest official scheme
guidelines and the sanctioning agency.

Architecture:
- schemes.py        → Scheme configuration and parameters
- calculations.py   → Core financial calculations (project cost, loan amount)
- emi.py            → Quarterly instalment & monthly EMI (reducing-balance)
- repayment.py      → Repayment schedule generation (quarterly primary, monthly secondary)
- validation.py     → Input validation and scheme limit checking
"""

from .schemes import (
    SCHEMES,
    MICRO_FINANCE_SCHEME,
    TERM_LOAN_SCHEME,
    select_scheme,
)
from .calculations import (
    calculate_project_cost,
    calculate_loan_amount,
    calculate_margin_from_project_cost,
)
from .emi import (
    calculate_quarterly_instalment,
    calculate_monthly_emi_reference,
    calculate_emi,
    QuarterlyInstalmentResult,
    MonthlyEMIResult,
)
from .repayment import (
    generate_quarterly_schedule,
    generate_monthly_schedule,
    generate_repayment_schedule,
    generate_quarterly_summary,
    aggregate_monthly_to_quarterly,
    QuarterlyPaymentEntry,
    MonthlyPaymentEntry,
    QuarterlyAggregate,
)
from .validation import (
    validate_margin,
    check_scheme_limits,
    ValidationResult,
)

__all__ = [
    # Schemes
    "SCHEMES",
    "MICRO_FINANCE_SCHEME",
    "TERM_LOAN_SCHEME",
    "select_scheme",
    # Calculations
    "calculate_project_cost",
    "calculate_loan_amount",
    "calculate_margin_from_project_cost",
    # Quarterly Instalment (PRIMARY)
    "calculate_quarterly_instalment",
    "QuarterlyInstalmentResult",
    # Monthly EMI (reference only)
    "calculate_monthly_emi_reference",
    "calculate_emi",
    "MonthlyEMIResult",
    # Repayment Schedules
    "generate_quarterly_schedule",
    "generate_monthly_schedule",
    "generate_repayment_schedule",
    "generate_quarterly_summary",
    "aggregate_monthly_to_quarterly",
    "QuarterlyPaymentEntry",
    "MonthlyPaymentEntry",
    "QuarterlyAggregate",
    # Validation
    "validate_margin",
    "check_scheme_limits",
    "ValidationResult",
]
