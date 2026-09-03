"""
Input Validation & Scheme Limit Checking

Provides functions for validating user input and checking whether
calculated values fall within scheme limits.
"""

from dataclasses import dataclass
from typing import Optional
from .schemes import MAX_SUPPORTED_PROJECT_COST, MAX_SUPPORTED_LOAN_AMOUNT


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating user margin capital input.

    Attributes:
        is_valid: Whether the input passed validation.
        value: The parsed numeric value (None if invalid).
        error_message: Description of the validation error (None if valid).
    """

    is_valid: bool
    value: Optional[float]
    error_message: Optional[str]


def validate_margin(raw_input: str) -> ValidationResult:
    """Validate the user's margin capital input.

    Checks:
    - Empty input → error
    - Non-numeric input → error
    - Zero → error
    - Negative → error
    - Valid positive number → success

    Args:
        raw_input: The raw string from the user input field.

    Returns:
        ValidationResult with validation status and parsed value or error.
    """
    if raw_input is None:
        return ValidationResult(
            is_valid=False,
            value=None,
            error_message="Please enter your available margin capital.",
        )

    stripped = raw_input.strip()

    if not stripped:
        return ValidationResult(
            is_valid=False,
            value=None,
            error_message="Please enter your available margin capital.",
        )

    # Remove Indian currency symbols and commas for parsing
    cleaned = stripped.replace("₹", "").replace(",", "").replace(" ", "")

    try:
        value = float(cleaned)
    except (ValueError, TypeError):
        return ValidationResult(
            is_valid=False,
            value=None,
            error_message="Please enter a valid number (e.g., 100000).",
        )

    if value == 0:
        return ValidationResult(
            is_valid=False,
            value=0.0,
            error_message="Margin capital must be greater than zero.",
        )

    if value < 0:
        return ValidationResult(
            is_valid=False,
            value=value,
            error_message="Margin capital cannot be negative.",
        )

    return ValidationResult(is_valid=True, value=value, error_message=None)


@dataclass(frozen=True)
class SchemeLimitResult:
    """Result of checking whether a project cost is within scheme limits.

    Attributes:
        within_limits: Whether the project cost is within supported limits.
        exceeds_limit: Whether the cost exceeds maximum supported limits.
        max_project_cost: Maximum supported project cost.
        max_loan_amount: Maximum supported loan amount.
        warning_message: Warning text if limits are exceeded.
    """

    within_limits: bool
    exceeds_limit: bool
    max_project_cost: float
    max_loan_amount: float
    warning_message: Optional[str]


def check_scheme_limits(project_cost: float) -> SchemeLimitResult:
    """Check if the calculated project cost is within scheme limits.

    If the project cost exceeds the maximum supported amount across all
    schemes, a warning is generated.

    Args:
        project_cost: Calculated project cost in ₹.

    Returns:
        SchemeLimitResult with limit status and optional warning.
    """
    if project_cost <= MAX_SUPPORTED_PROJECT_COST:
        return SchemeLimitResult(
            within_limits=True,
            exceeds_limit=False,
            max_project_cost=MAX_SUPPORTED_PROJECT_COST,
            max_loan_amount=MAX_SUPPORTED_LOAN_AMOUNT,
            warning_message=None,
        )

    return SchemeLimitResult(
        within_limits=False,
        exceeds_limit=True,
        max_project_cost=MAX_SUPPORTED_PROJECT_COST,
        max_loan_amount=MAX_SUPPORTED_LOAN_AMOUNT,
        warning_message=(
            "Your calculated project cost is outside the supported "
            "project-cost range. "
            f"Maximum supported project cost: ₹{MAX_SUPPORTED_PROJECT_COST:,.0f}. "
            f"Maximum stated loan amount: ₹{MAX_SUPPORTED_LOAN_AMOUNT:,.0f}."
        ),
    )
