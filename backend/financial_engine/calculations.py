"""
Core Financial Calculations

Provides deterministic functions for calculating project cost, loan amount,
and margin from project cost. All math is pure and has no side effects.

Assumption (from the SIH problem statement):
- The beneficiary contributes approximately 10% of the project cost.
- The funding agency provides up to 90% as a concessional loan.
"""

from .schemes import FinancingScheme, select_scheme


# Contribution percentage (beneficiary's share)
CONTRIBUTION_PERCENTAGE = 0.10  # 10%

# Funding percentage (agency's share)
FUNDING_PERCENTAGE = 0.90  # 90%


def calculate_project_cost(margin_capital: float) -> float:
    """Calculate the total project cost from the user's available margin capital.

    Formula:
        Project Cost = Available Margin Capital / Contribution Percentage

    This assumes the user's margin capital represents 10% of the total
    project cost (as stated in the SIH problem statement).

    Args:
        margin_capital: The beneficiary's available contribution in ₹.
                       Must be a positive number.

    Returns:
        Total project cost in ₹.

    Raises:
        ValueError: If margin_capital is not positive.

    Examples:
        >>> calculate_project_cost(1_00_000)
        10_00_000.0
        >>> calculate_project_cost(14_000)
        1_40_000.0
    """
    if margin_capital <= 0:
        raise ValueError("Margin capital must be a positive number.")
    return margin_capital / CONTRIBUTION_PERCENTAGE


def calculate_loan_amount(project_cost: float, scheme: FinancingScheme) -> float:
    """Calculate the loan amount for a given project cost and scheme.

    The loan is calculated as:
        Calculated Loan = Project Cost × Funding Percentage

    Then capped at the scheme's maximum loan amount.

    Args:
        project_cost: Total project cost in ₹.
        scheme: The applicable FinancingScheme.

    Returns:
        Loan amount in ₹ (capped at scheme maximum).

    Raises:
        ValueError: If project_cost is negative.
    """
    if project_cost < 0:
        raise ValueError("Project cost cannot be negative.")

    calculated_loan = project_cost * scheme.funding_percentage
    # Cap at the scheme's maximum loan amount
    return min(calculated_loan, scheme.max_loan_amount)


def calculate_margin_from_project_cost(project_cost: float) -> float:
    """Calculate the required margin capital from a known project cost.

    Formula:
        Margin Capital = Project Cost × Contribution Percentage

    Args:
        project_cost: Total project cost in ₹.

    Returns:
        Required margin capital in ₹.

    Raises:
        ValueError: If project_cost is negative.
    """
    if project_cost < 0:
        raise ValueError("Project cost cannot be negative.")
    return project_cost * CONTRIBUTION_PERCENTAGE


def get_loan_for_project_cost(project_cost: float) -> float:
    """High-level function: select scheme and calculate loan.

    Selects the appropriate scheme for the given project cost, then
    calculates the loan amount. If no scheme is available, returns 0.

    Args:
        project_cost: Total project cost in ₹.

    Returns:
        Loan amount in ₹, or 0 if no scheme is available.

    Examples:
        >>> get_loan_for_project_cost(10_00_000)
        45_00_000  # Capped at Term Loan scheme max
    """
    scheme = select_scheme(project_cost)
    if scheme is None:
        return 0.0
    return calculate_loan_amount(project_cost, scheme)
