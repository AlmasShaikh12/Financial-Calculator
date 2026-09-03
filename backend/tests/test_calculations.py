"""
Comprehensive Tests for the SIH Financial Engine (Moratorium-Adjusted)

Tests cover:
1. Validation (empty, zero, negative, text, currency formatting)
2. Scheme selection (boundary at ₹1.4L, ₹50L)
3. Core calculations (project cost, loan amount)
4. Loan cap enforcement (₹1.25L micro, ₹45L term)
5. Quarterly instalment (moratorium-adjusted N)
6. Monthly EMI reference (moratorium-adjusted)
7. Quarterly repayment schedule (full tenure with moratorium rows)
8. Monthly repayment schedule (correct length)
9. End-to-end flows

Moratorium-adjusted repayment quarters:
- Term Loan: 7 years = 28 quarters − 2 moratorium quarters = 26 repayment quarters
- Micro Finance: 3 years = 12 quarters − 1 moratorium quarter = 11 repayment quarters

Schedule structure:
- Schedule has total_scheme_quarters rows (28 for Term Loan, 12 for Micro Finance)
- First moratorium_quarters rows = "moratorium" status
- Remaining rows = "repayment" status

Source: MoSJE Annual Report 2025-26 — NSFDC schemes.

IMPORTANT: These tests validate the deterministic financial engine only.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import the engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from financial_engine import (
    calculate_emi,
    generate_repayment_schedule,
    generate_quarterly_summary,
)
from financial_engine.schemes import (
    MICRO_FINANCE_SCHEME,
    TERM_LOAN_SCHEME,
    select_scheme,
    MAX_SUPPORTED_PROJECT_COST,
    MAX_SUPPORTED_LOAN_AMOUNT,
)
from financial_engine.calculations import (
    calculate_project_cost,
    calculate_loan_amount,
    calculate_margin_from_project_cost,
    CONTRIBUTION_PERCENTAGE,
    FUNDING_PERCENTAGE,
)
from financial_engine.emi import (
    calculate_quarterly_instalment,
    calculate_monthly_emi_reference,
    QuarterlyInstalmentResult,
    MonthlyEMIResult,
)
from financial_engine.repayment import (
    generate_quarterly_schedule,
    generate_monthly_schedule,
    aggregate_monthly_to_quarterly,
    QuarterlyPaymentEntry,
    MonthlyPaymentEntry,
    QuarterlyAggregate,
)
from financial_engine.validation import (
    validate_margin,
    check_scheme_limits,
)


# ===========================================================================
# Validation Tests
# ===========================================================================

class TestApiCompatibility:
    """Ensures the API-facing helper names remain available."""

    def test_compatibility_helpers_exist(self):
        scheme = MICRO_FINANCE_SCHEME
        emi = calculate_emi(100000, scheme)
        assert emi.monthly_emi > 0

        schedule = generate_repayment_schedule(100000, scheme)
        assert len(schedule) > 0
        assert schedule[0].month == 1

        summary = generate_quarterly_summary(schedule)
        assert len(summary) > 0


class TestValidateMargin:
    """Tests for user input validation."""

    def test_empty_input(self):
        result = validate_margin("")
        assert result.is_valid is False
        assert "enter" in result.error_message.lower()

    def test_none_input(self):
        result = validate_margin(None)
        assert result.is_valid is False

    def test_whitespace_only(self):
        result = validate_margin("   ")
        assert result.is_valid is False

    def test_zero(self):
        result = validate_margin("0")
        assert result.is_valid is False
        assert "greater than zero" in result.error_message.lower()

    def test_negative(self):
        result = validate_margin("-5000")
        assert result.is_valid is False
        assert "negative" in result.error_message.lower()

    def test_invalid_text(self):
        result = validate_margin("abc")
        assert result.is_valid is False
        assert "valid number" in result.error_message.lower()

    def test_mixed_invalid(self):
        result = validate_margin("abc123")
        assert result.is_valid is False

    def test_valid_integer(self):
        result = validate_margin("100000")
        assert result.is_valid is True
        assert result.value == 100000.0

    def test_valid_decimal(self):
        result = validate_margin("100000.50")
        assert result.is_valid is True
        assert result.value == 100000.50

    def test_indian_currency_symbol(self):
        result = validate_margin("₹100000")
        assert result.is_valid is True
        assert result.value == 100000.0

    def test_commas(self):
        result = validate_margin("1,00,000")
        assert result.is_valid is True
        assert result.value == 100000.0

    def test_currency_with_commas(self):
        result = validate_margin("₹1,00,000")
        assert result.is_valid is True
        assert result.value == 100000.0

    def test_spaces(self):
        result = validate_margin(" 100000 ")
        assert result.is_valid is True
        assert result.value == 100000.0


# ===========================================================================
# Scheme Selection Tests
# ===========================================================================

class TestSchemeSelection:
    """Tests for automatic scheme selection."""

    def test_micro_finance_below_limit(self):
        """₹10,000 margin → ₹1,00,000 project cost → Micro Finance."""
        project_cost = calculate_project_cost(10_000)
        assert project_cost == 1_00_000
        scheme = select_scheme(project_cost)
        assert scheme == MICRO_FINANCE_SCHEME

    def test_micro_finance_at_upper_boundary(self):
        """₹14,000 margin → ₹1,40,000 project cost → Micro Finance (boundary)."""
        project_cost = calculate_project_cost(14_000)
        assert project_cost == 1_40_000
        scheme = select_scheme(project_cost)
        assert scheme == MICRO_FINANCE_SCHEME
        assert scheme.name == "Micro Finance Scheme"

    def test_term_loan_just_above_boundary(self):
        """₹14,001 margin → ₹1,40,010 project cost → Term Loan."""
        project_cost = calculate_project_cost(14_001)
        assert project_cost == 1_40_010
        scheme = select_scheme(project_cost)
        assert scheme == TERM_LOAN_SCHEME

    def test_term_loan_typical(self):
        """₹15,000 margin → ₹1,50,000 project cost → Term Loan."""
        project_cost = calculate_project_cost(15_000)
        assert project_cost == 1_50_000
        scheme = select_scheme(project_cost)
        assert scheme == TERM_LOAN_SCHEME

    def test_term_loan_large(self):
        """₹1,00,000 margin → ₹10,00,000 project cost → Term Loan."""
        project_cost = calculate_project_cost(1_00_000)
        assert project_cost == 10_00_000
        scheme = select_scheme(project_cost)
        assert scheme == TERM_LOAN_SCHEME

    def test_term_loan_at_max_boundary(self):
        """₹5,00,000 margin → ₹50,00,000 project cost → Term Loan (boundary)."""
        project_cost = calculate_project_cost(5_00_000)
        assert project_cost == 50_00_000
        scheme = select_scheme(project_cost)
        assert scheme == TERM_LOAN_SCHEME
        assert scheme.name == "Term Loan Scheme"

    def test_no_scheme_beyond_limit(self):
        """₹5,00,001 margin → ₹50,00,010 project cost → No scheme."""
        project_cost = calculate_project_cost(5_00_001)
        assert project_cost > 50_00_000
        scheme = select_scheme(project_cost)
        assert scheme is None

    def test_zero_project_cost(self):
        """Zero project cost → matches Micro Finance (0 ≤ 1,40,000)."""
        scheme = select_scheme(0)
        assert scheme == MICRO_FINANCE_SCHEME

    def test_negative_project_cost_raises(self):
        """Negative project cost → ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            select_scheme(-1000)


# ===========================================================================
# Core Calculation Tests
# ===========================================================================

class TestCoreCalculations:
    """Tests for project cost and loan amount calculations."""

    def test_project_cost_formula(self):
        """Verify: Project Cost = Margin / 0.10."""
        assert calculate_project_cost(10_000) == 1_00_000
        assert calculate_project_cost(1_00_000) == 10_00_000
        assert calculate_project_cost(5_00_000) == 50_00_000

    def test_project_cost_small_amount(self):
        """₹1,000 margin → ₹10,000 project cost."""
        assert calculate_project_cost(1_000) == 10_000

    def test_project_cost_invalid(self):
        """Zero and negative margin should raise."""
        with pytest.raises(ValueError):
            calculate_project_cost(0)
        with pytest.raises(ValueError):
            calculate_project_cost(-1000)

    def test_margin_from_project_cost(self):
        """Verify reverse calculation: Margin = Project Cost × 0.10."""
        assert calculate_margin_from_project_cost(10_00_000) == 1_00_000
        assert calculate_margin_from_project_cost(1_40_000) == 14_000
        assert calculate_margin_from_project_cost(50_00_000) == 5_00_000


# ===========================================================================
# Loan Amount Tests — including boundary cap tests
# ===========================================================================

class TestLoanAmount:
    """Tests for loan amount calculation with scheme capping."""

    def test_micro_finance_boundary_cap(self):
        """₹1,40,000 project cost → 90% = ₹1,26,000 but CAPPED at ₹1,25,000."""
        project_cost = 1_40_000
        loan = calculate_loan_amount(project_cost, MICRO_FINANCE_SCHEME)
        # 1,40,000 × 0.90 = 1,26,000 but max is 1,25,000
        assert loan == 1_25_000

    def test_micro_finance_small_project(self):
        """Small project: ₹1,00,000 cost → ₹90,000 loan (within limit)."""
        loan = calculate_loan_amount(1_00_000, MICRO_FINANCE_SCHEME)
        assert loan == 90_000

    def test_term_loan_standard(self):
        """Term Loan: ₹10,00,000 cost → ₹9,00,000 loan."""
        loan = calculate_loan_amount(10_00_000, TERM_LOAN_SCHEME)
        assert loan == 9_00_000

    def test_term_loan_at_max_project(self):
        """Term Loan at max: ₹50,00,000 cost → 90% = ₹45,00,000 (matches cap)."""
        loan = calculate_loan_amount(50_00_000, TERM_LOAN_SCHEME)
        assert loan == 45_00_000

    def test_term_loan_beyond_max_project(self):
        """₹60,00,000 cost → 90% = ₹54,00,000 but capped at ₹45,00,000."""
        loan = calculate_loan_amount(60_00_000, TERM_LOAN_SCHEME)
        assert loan == 45_00_000

    def test_loan_negative_project_cost(self):
        """Negative project cost should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            calculate_loan_amount(-1000, MICRO_FINANCE_SCHEME)


# ===========================================================================
# Scheme Parameter Tests
# ===========================================================================

class TestSchemeParameters:
    """Verify scheme parameters match MoSJE Annual Report 2025-26."""

    def test_micro_finance_params(self):
        assert MICRO_FINANCE_SCHEME.max_project_cost == 1_40_000
        assert MICRO_FINANCE_SCHEME.max_loan_amount == 1_25_000
        assert MICRO_FINANCE_SCHEME.interest_rate_annual == 0.065
        assert MICRO_FINANCE_SCHEME.tenure_years == 3
        assert MICRO_FINANCE_SCHEME.moratorium_months == 3
        assert MICRO_FINANCE_SCHEME.funding_percentage == 0.90
        assert MICRO_FINANCE_SCHEME.repayment_frequency == "quarterly"

    def test_term_loan_params(self):
        assert TERM_LOAN_SCHEME.max_project_cost == 50_00_000
        assert TERM_LOAN_SCHEME.max_loan_amount == 45_00_000
        assert TERM_LOAN_SCHEME.interest_rate_annual == 0.08
        assert TERM_LOAN_SCHEME.tenure_years == 7
        assert TERM_LOAN_SCHEME.moratorium_months == 6
        assert TERM_LOAN_SCHEME.funding_percentage == 0.90
        assert TERM_LOAN_SCHEME.repayment_frequency == "quarterly"

    def test_term_loan_extended_moratorium(self):
        """Term Loan: 12-month extended moratorium for plantation/construction."""
        assert TERM_LOAN_SCHEME.extended_moratorium_months == 12

    def test_micro_finance_no_extended_moratorium(self):
        """Micro Finance: no extended moratorium stated."""
        assert MICRO_FINANCE_SCHEME.extended_moratorium_months == 0

    def test_max_supported_values(self):
        assert MAX_SUPPORTED_PROJECT_COST == 50_00_000
        assert MAX_SUPPORTED_LOAN_AMOUNT == 45_00_000

    def test_source_references_exist(self):
        """Both schemes should have source references."""
        assert MICRO_FINANCE_SCHEME.source_reference != ""
        assert TERM_LOAN_SCHEME.source_reference != ""


# ===========================================================================
# Moratorium-Adjusted Quarterly Instalment Tests (PRIMARY)
# ===========================================================================

class TestQuarterlyInstalment:
    """Tests for the quarterly instalment calculator (moratorium-adjusted)."""

    def test_term_loan_repayment_quarters(self):
        """Term Loan: 7 years = 28 quarters − 2 moratorium = 26 repayment quarters."""
        result = calculate_quarterly_instalment(9_00_000, TERM_LOAN_SCHEME)
        assert result.total_scheme_quarters == 28  # 7 years × 4
        assert result.moratorium_quarters == 2     # 6 months / 3
        assert result.repayment_quarters == 26     # 28 − 2

    def test_micro_finance_repayment_quarters(self):
        """Micro Finance: 3 years = 12 quarters − 1 moratorium = 11 repayment quarters."""
        result = calculate_quarterly_instalment(1_25_000, MICRO_FINANCE_SCHEME)
        assert result.total_scheme_quarters == 12  # 3 years × 4
        assert result.moratorium_quarters == 1     # 3 months / 3
        assert result.repayment_quarters == 11     # 12 − 1

    def test_term_loan_quarterly_basic(self):
        """₹9,00,000 loan at 8% for 26 repayment quarters → instalment ≈ ₹44,729."""
        result = calculate_quarterly_instalment(9_00_000, TERM_LOAN_SCHEME)
        assert result.loan_amount == 9_00_000
        assert result.annual_interest_rate == 0.08
        assert result.quarterly_interest_rate == 0.02  # 8% / 4
        assert result.repayment_quarters == 26
        assert result.moratorium_months == 6
        assert result.extended_moratorium_months == 12
        assert result.repayment_frequency == "quarterly"
        # Verify quarterly instalment is approximately correct
        assert 44_000 <= result.quarterly_instalment <= 45_500
        assert result.total_repayment > result.loan_amount
        assert result.total_interest > 0

    def test_micro_finance_quarterly(self):
        """₹1,25,000 loan at 6.5% for 11 repayment quarters → quarterly instalment."""
        result = calculate_quarterly_instalment(1_25_000, MICRO_FINANCE_SCHEME)
        assert result.loan_amount == 1_25_000
        assert result.annual_interest_rate == 0.065
        assert result.quarterly_interest_rate == pytest.approx(0.01625)
        assert result.repayment_quarters == 11
        assert result.quarterly_instalment > 0
        assert result.total_repayment > result.loan_amount

    def test_quarterly_instalment_zero_raises(self):
        """Zero loan amount should raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            calculate_quarterly_instalment(0, TERM_LOAN_SCHEME)

    def test_quarterly_instalment_negative_raises(self):
        """Negative loan amount should raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            calculate_quarterly_instalment(-100, TERM_LOAN_SCHEME)

    def test_quarterly_total_consistency(self):
        """total_repayment ≈ repayment_quarters × quarterly_instalment (within rounding)."""
        result = calculate_quarterly_instalment(9_00_000, TERM_LOAN_SCHEME)
        computed_total = result.quarterly_instalment * result.repayment_quarters
        assert abs(result.total_repayment - computed_total) < 1.0
        assert abs(result.total_interest - (result.total_repayment - result.loan_amount)) < 0.01


# ===========================================================================
# Monthly EMI Reference Tests (SECONDARY)
# ===========================================================================

class TestMonthlyEMIReference:
    """Tests for the monthly EMI reference (moratorium-adjusted, NOT scheme repayment)."""

    def test_monthly_emi_basic(self):
        """₹9,00,000 loan at 8% for 78 repayment months → monthly EMI."""
        result = calculate_monthly_emi_reference(9_00_000, TERM_LOAN_SCHEME)
        assert result.loan_amount == 9_00_000
        # 7 years = 84 months − 6 moratorium months = 78 repayment months
        assert result.total_months == 78
        assert result.monthly_emi > 0

    def test_monthly_emi_micro_finance(self):
        """₹1,25,000 loan at 6.5% for 33 repayment months."""
        result = calculate_monthly_emi_reference(1_25_000, MICRO_FINANCE_SCHEME)
        # 3 years = 36 months − 3 moratorium months = 33 repayment months
        assert result.total_months == 33
        assert result.monthly_emi > 0

    def test_monthly_emi_zero_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            calculate_monthly_emi_reference(0, TERM_LOAN_SCHEME)


# ===========================================================================
# Quarterly Schedule Tests (PRIMARY — full tenure with moratorium rows)
# ===========================================================================

class TestQuarterlySchedule:
    """Tests for the primary quarterly repayment schedule.

    The schedule now covers the FULL scheme tenure and includes moratorium rows:
    - Term Loan: 28 total rows (2 moratorium + 26 repayment)
    - Micro Finance: 12 total rows (1 moratorium + 11 repayment)
    """

    def test_schedule_length_term_loan(self):
        """Schedule should have 28 entries (full tenure: 2 moratorium + 26 repayment)."""
        schedule = generate_quarterly_schedule(9_00_000, TERM_LOAN_SCHEME)
        assert len(schedule) == 28

    def test_schedule_length_micro_finance(self):
        """Schedule should have 12 entries (full tenure: 1 moratorium + 11 repayment)."""
        schedule = generate_quarterly_schedule(1_25_000, MICRO_FINANCE_SCHEME)
        assert len(schedule) == 12

    def test_moratorium_rows_term_loan(self):
        """First 2 rows should be moratorium status."""
        schedule = generate_quarterly_schedule(9_00_000, TERM_LOAN_SCHEME)
        for i in range(2):
            assert schedule[i].status == "moratorium"
            assert schedule[i].repayment_number is None
            assert schedule[i].instalment == 0.0
            assert schedule[i].principal_component == 0.0
            assert schedule[i].interest_component is None
            assert schedule[i].opening_balance == schedule[i].closing_balance

    def test_moratorium_rows_micro_finance(self):
        """First 1 row should be moratorium status."""
        schedule = generate_quarterly_schedule(1_25_000, MICRO_FINANCE_SCHEME)
        assert schedule[0].status == "moratorium"
        assert schedule[0].repayment_number is None
        assert schedule[0].instalment == 0.0
        assert schedule[0].opening_balance == schedule[0].closing_balance

    def test_repayment_rows_term_loan(self):
        """Rows 3-28 should be repayment status (repayment_number 1-26)."""
        schedule = generate_quarterly_schedule(9_00_000, TERM_LOAN_SCHEME)
        for i in range(2, 28):
            assert schedule[i].status == "repayment"
            assert schedule[i].repayment_number == i - 1  # 1-indexed after moratorium
            assert schedule[i].instalment > 0
            assert schedule[i].principal_component > 0
            assert schedule[i].interest_component is not None

    def test_first_repayment_starts_at_loan_amount(self):
        """First repayment row (Q3) should open at the loan amount."""
        schedule = generate_quarterly_schedule(9_00_000, TERM_LOAN_SCHEME)
        assert schedule[2].opening_balance == 9_00_000

    def test_last_quarter_ends_at_zero(self):
        """Last repayment row should close at zero."""
        schedule = generate_quarterly_schedule(9_00_000, TERM_LOAN_SCHEME)
        assert schedule[-1].closing_balance == 0.0

    def test_balance_decreases_monotonically_during_repayment(self):
        """Balance should decrease only during repayment rows."""
        schedule = generate_quarterly_schedule(9_00_000, TERM_LOAN_SCHEME)
        # During moratorium, balance stays the same
        for i in range(2):
            assert schedule[i].closing_balance == schedule[i].opening_balance
        # During repayment, balance decreases
        for i in range(2, len(schedule)):
            assert schedule[i].closing_balance <= schedule[i].opening_balance

    def test_principal_plus_interest_equals_instalment(self):
        """For repayment rows, principal + interest = instalment."""
        schedule = generate_quarterly_schedule(9_00_000, TERM_LOAN_SCHEME)
        for entry in schedule:
            if entry.status == "repayment":
                assert entry.principal_component + entry.interest_component == pytest.approx(
                    entry.instalment, abs=0.02
                )

    def test_total_principal_equals_loan(self):
        """Sum of all principal components should equal the loan amount."""
        schedule = generate_quarterly_schedule(9_00_000, TERM_LOAN_SCHEME)
        total_principal = sum(e.principal_component for e in schedule)
        assert total_principal == pytest.approx(9_00_000, abs=1.0)

    def test_micro_finance_total_principal_equals_loan(self):
        """Sum of all principal components for micro finance should equal loan."""
        schedule = generate_quarterly_schedule(1_25_000, MICRO_FINANCE_SCHEME)
        total_principal = sum(e.principal_component for e in schedule)
        assert total_principal == pytest.approx(1_25_000, abs=1.0)

    def test_quarter_numbers_are_sequential(self):
        """Quarter numbers should be 1 through total_scheme_quarters."""
        schedule = generate_quarterly_schedule(9_00_000, TERM_LOAN_SCHEME)
        for i, entry in enumerate(schedule):
            assert entry.quarter == i + 1

    def test_empty_schedule(self):
        with pytest.raises(ValueError):
            generate_quarterly_schedule(0, TERM_LOAN_SCHEME)


# ===========================================================================
# Monthly Schedule Tests (SECONDARY)
# ===========================================================================

class TestMonthlySchedule:
    """Tests for the optional monthly repayment breakdown."""

    def test_schedule_length(self):
        """78 months (84 − 6 moratorium)."""
        schedule = generate_monthly_schedule(9_00_000, TERM_LOAN_SCHEME)
        assert len(schedule) == 78

    def test_first_month_starts_at_loan_amount(self):
        schedule = generate_monthly_schedule(9_00_000, TERM_LOAN_SCHEME)
        assert schedule[0].opening_balance == 9_00_000

    def test_last_month_ends_at_zero(self):
        schedule = generate_monthly_schedule(9_00_000, TERM_LOAN_SCHEME)
        assert schedule[-1].closing_balance == 0.0

    def test_aggregate_to_quarterly(self):
        """Aggregating 78 monthly entries should give 26 quarterly entries."""
        schedule = generate_monthly_schedule(9_00_000, TERM_LOAN_SCHEME)
        quarterly = aggregate_monthly_to_quarterly(schedule)
        assert len(quarterly) == 26

    def test_quarterly_remaining_decreases(self):
        schedule = generate_monthly_schedule(9_00_000, TERM_LOAN_SCHEME)
        quarterly = aggregate_monthly_to_quarterly(schedule)
        for i in range(1, len(quarterly)):
            assert quarterly[i].remaining_loan <= quarterly[i - 1].remaining_loan


# ===========================================================================
# End-to-End Integration Tests
# ===========================================================================

class TestEndToEnd:
    """Integration test: full flow from margin input to results."""

    def test_full_flow_100000(self):
        """₹1,00,000 margin → full calculation pipeline."""
        validation = validate_margin("100000")
        assert validation.is_valid is True
        margin = validation.value

        project_cost = calculate_project_cost(margin)
        assert project_cost == 10_00_000

        limits = check_scheme_limits(project_cost)
        assert limits.exceeds_limit is False

        scheme = select_scheme(project_cost)
        assert scheme == TERM_LOAN_SCHEME

        loan = calculate_loan_amount(project_cost, scheme)
        assert loan == 9_00_000

        # Primary: quarterly instalment (26 repayment quarters)
        qi = calculate_quarterly_instalment(loan, scheme)
        assert qi.quarterly_instalment > 0
        assert qi.repayment_quarters == 26
        assert qi.moratorium_quarters == 2
        assert qi.total_scheme_quarters == 28

        # Primary schedule (28 entries = 2 moratorium + 26 repayment)
        q_schedule = generate_quarterly_schedule(loan, scheme)
        assert len(q_schedule) == 28
        assert q_schedule[0].status == "moratorium"
        assert q_schedule[1].status == "moratorium"
        assert q_schedule[2].status == "repayment"
        assert q_schedule[2].repayment_number == 1
        assert q_schedule[-1].closing_balance == 0.0

        # Secondary: monthly reference (78 months)
        emi = calculate_monthly_emi_reference(loan, scheme)
        assert emi.monthly_emi > 0
        assert emi.total_months == 78

    def test_full_flow_600000_exceeds(self):
        """₹6,00,000 margin → ₹60,00,000 project cost → outside supported range."""
        margin = 6_00_000
        project_cost = calculate_project_cost(margin)
        assert project_cost == 60_00_000

        limits = check_scheme_limits(project_cost)
        assert limits.exceeds_limit is True
        assert limits.warning_message is not None
        assert "outside" in limits.warning_message.lower()

        scheme = select_scheme(project_cost)
        assert scheme is None

    def test_full_flow_boundary_14000(self):
        """₹14,000 margin → ₹1,40,000 project cost → Micro Finance (exact boundary)."""
        margin = 14_000
        project_cost = calculate_project_cost(margin)
        assert project_cost == 1_40_000

        scheme = select_scheme(project_cost)
        assert scheme == MICRO_FINANCE_SCHEME

        loan = calculate_loan_amount(project_cost, scheme)
        assert loan == 1_25_000  # Capped

        qi = calculate_quarterly_instalment(loan, scheme)
        assert qi.quarterly_instalment > 0
        assert qi.repayment_quarters == 11  # 12 − 1 moratorium
        assert qi.moratorium_quarters == 1

        q_schedule = generate_quarterly_schedule(loan, scheme)
        assert len(q_schedule) == 12  # Full tenure: 1 moratorium + 11 repayment
        assert q_schedule[0].status == "moratorium"
        assert q_schedule[1].status == "repayment"
        assert q_schedule[1].repayment_number == 1

    def test_full_flow_boundary_50_lakh(self):
        """₹5,00,000 margin → ₹50,00,000 project cost → Term Loan (exact boundary)."""
        margin = 5_00_000
        project_cost = calculate_project_cost(margin)
        assert project_cost == 50_00_000

        scheme = select_scheme(project_cost)
        assert scheme == TERM_LOAN_SCHEME

        loan = calculate_loan_amount(project_cost, scheme)
        assert loan == 45_00_000  # 90% of 50L = 45L (matches cap)

        qi = calculate_quarterly_instalment(loan, scheme)
        assert qi.quarterly_instalment > 0
        assert qi.repayment_quarters == 26  # 28 − 2 moratorium

    def test_full_flow_micro_finance_small(self):
        """₹10,000 margin → ₹1,00,000 project cost → Micro Finance."""
        margin = 10_000
        project_cost = calculate_project_cost(margin)
        assert project_cost == 1_00_000

        scheme = select_scheme(project_cost)
        assert scheme == MICRO_FINANCE_SCHEME

        loan = calculate_loan_amount(project_cost, scheme)
        assert loan == 90_000

        qi = calculate_quarterly_instalment(loan, scheme)
        assert qi.repayment_quarters == 11  # 12 − 1 moratorium
        assert qi.quarterly_instalment > 0

        q_schedule = generate_quarterly_schedule(loan, scheme)
        assert len(q_schedule) == 12  # 1 moratorium + 11 repayment
        assert q_schedule[0].status == "moratorium"
        assert q_schedule[-1].closing_balance == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
