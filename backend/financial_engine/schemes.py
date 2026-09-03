"""
Scheme Configuration Module

Defines the financing schemes as described in the SIH problem statement.
All parameters are configurable and clearly documented.

Source: Ministry of Social Justice & Empowerment Annual Report 2025-26
(National Scheduled Castes Finance & Development Corporation — NSFDC schemes)

IMPORTANT DISCLAIMER:
These parameters are based on the SIH problem statement and verified against
the MoSJE Annual Report 2025-26. Actual eligibility, sanction, and repayment
terms are subject to the latest official guidelines and the sanctioning agency.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FinancingScheme:
    """Configuration for a single financing scheme.

    All monetary values are in Indian Rupees (₹).

    Attributes:
        name: Human-readable scheme name.
        description: Brief description of the scheme.
        max_project_cost: Maximum eligible project cost.
        funding_percentage: Percentage of project cost funded (0.0 to 1.0).
        max_loan_amount: Absolute maximum loan amount (cap).
        interest_rate_annual: Annual interest rate as a decimal (e.g., 0.08 for 8%).
        tenure_years: Loan tenure in years.
        moratorium_months: Standard moratorium period in months.
        extended_moratorium_months: Extended moratorium for plantation/construction.
        min_project_cost: Minimum project cost (0 means no minimum).
        repayment_frequency: How repayments are collected ("quarterly").
        source_reference: Where these parameters come from.
    """

    name: str
    description: str
    max_project_cost: float
    funding_percentage: float
    max_loan_amount: float
    interest_rate_annual: float
    tenure_years: int
    moratorium_months: int
    min_project_cost: float = 0.0
    extended_moratorium_months: int = 0
    repayment_frequency: str = "quarterly"
    source_reference: str = ""


# ---------------------------------------------------------------------------
# Scheme Definitions — from MoSJE Annual Report 2025-26 / SIH Problem Statement
# ---------------------------------------------------------------------------
# Source: Ministry of Social Justice & Empowerment Annual Report 2025-26
# (NSFDC concessional financing schemes)
#
# DISCLAIMER: These parameters are based on the SIH problem statement and
# verified against the MoSJE Annual Report 2025-26. Actual eligibility,
# sanction, and repayment terms are subject to the latest official
# guidelines and the sanctioning agency.
# ---------------------------------------------------------------------------

MICRO_FINANCE_SCHEME = FinancingScheme(
    name="Micro Finance Scheme",
    description=(
        "Concessional micro-finance for projects up to ₹1.40 lakh. "
        "Funding agency provides up to 90% as a concessional loan. "
        "Repayment in quarterly instalments within 3 years."
    ),
    max_project_cost=1_40_000,        # ₹1,40,000
    funding_percentage=0.90,           # 90%
    max_loan_amount=1_25_000,          # ₹1,25,000 (capped)
    interest_rate_annual=0.065,        # 6.5% p.a.
    tenure_years=3,
    moratorium_months=3,
    extended_moratorium_months=0,      # No extended moratorium stated
    min_project_cost=0.0,
    repayment_frequency="quarterly",
    source_reference=(
        "MoSJE Annual Report 2025-26 — NSFDC Micro Finance Scheme. "
        "Subject to verification against current official guidelines."
    ),
)

TERM_LOAN_SCHEME = FinancingScheme(
    name="Term Loan Scheme",
    description=(
        "Term loan for projects above ₹1.40 lakh and up to ₹50 lakh. "
        "Funding agency provides up to 90% as a concessional loan. "
        "Repayment in quarterly instalments within 7 years. "
        "Extended moratorium of 12 months for plantation and construction."
    ),
    max_project_cost=50_00_000,        # ₹50,00,000
    funding_percentage=0.90,           # 90%
    max_loan_amount=45_00_000,         # ₹45,00,000 (capped)
    interest_rate_annual=0.08,         # 8% p.a.
    tenure_years=7,
    moratorium_months=6,
    extended_moratorium_months=12,     # For plantation and construction
    min_project_cost=1_40_000,         # > ₹1,40,000 (exclusive)
    repayment_frequency="quarterly",
    source_reference=(
        "MoSJE Annual Report 2025-26 — NSFDC Term Loan Scheme. "
        "Subject to verification against current official guidelines."
    ),
)

# Registry of all schemes, ordered by project cost range (lowest first).
SCHEMES: list[FinancingScheme] = [
    MICRO_FINANCE_SCHEME,
    TERM_LOAN_SCHEME,
]

# Maximum supported project cost across all schemes
MAX_SUPPORTED_PROJECT_COST = max(s.max_project_cost for s in SCHEMES)

# Maximum supported loan amount across all schemes
MAX_SUPPORTED_LOAN_AMOUNT = max(s.max_loan_amount for s in SCHEMES)


def select_scheme(project_cost: float) -> Optional[FinancingScheme]:
    """Select the appropriate financing scheme based on project cost.

    Logic (from the MoSJE Annual Report 2025-26):
    - Project cost <= ₹1,40,000  → Micro Finance Scheme
    - ₹1,40,000 < Project cost <= ₹50,00,000  → Term Loan Scheme
    - Project cost > ₹50,00,000  → No scheme available

    Args:
        project_cost: Calculated project cost in ₹.

    Returns:
        The matching FinancingScheme, or None if no scheme covers the cost.

    Raises:
        ValueError: If project_cost is negative.
    """
    if project_cost < 0:
        raise ValueError("Project cost cannot be negative.")

    for scheme in SCHEMES:
        if project_cost <= scheme.max_project_cost:
            return scheme

    # Exceeds all scheme limits
    return None
