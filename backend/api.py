"""
SIH Financial Calculator — FastAPI Backend (Stub)

This module provides REST API endpoints for the financial engine.
It is a stub for future integration with the React frontend.

Endpoints:
    POST /calculate       → Full calculation from margin capital
    GET  /schemes          → List available schemes
    POST /validate         → Validate margin capital input
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from financial_engine import (
    calculate_project_cost,
    calculate_loan_amount,
    select_scheme,
    calculate_emi,
    generate_repayment_schedule,
    generate_quarterly_summary,
    validate_margin,
    check_scheme_limits,
    SCHEMES,
)

app = FastAPI(
    title="SIH Financial Calculator API",
    description=(
        "Reliable Financial Calculator & Scheme Router for the SIH "
        "financing model. DISCLAIMER: All calculations are based on the "
        "SIH problem statement and are for advisory/illustrative purposes."
    ),
    version="0.1.0",
)


# ---- Request / Response Models ----


class CalculateRequest(BaseModel):
    """Request body for the /calculate endpoint."""

    margin_capital: float


class SchemeInfo(BaseModel):
    """Scheme information returned in responses."""

    name: str
    description: str
    max_project_cost: float
    max_loan_amount: float
    interest_rate_annual: float
    tenure_years: int
    moratorium_months: int


class EMIInfo(BaseModel):
    """EMI calculation result."""

    monthly_emi: float
    total_repayment: float
    total_interest: float
    total_months: int
    moratorium_months: int


class RepaymentEntryResponse(BaseModel):
    """Monthly repayment entry."""

    month: int
    opening_balance: float
    emi_amount: float
    principal_component: float
    interest_component: float
    closing_balance: float


class QuarterlySummaryResponse(BaseModel):
    """Quarterly repayment summary."""

    quarter: int
    start_month: int
    end_month: int
    principal_paid: float
    interest_paid: float
    total_payment: float
    remaining_loan: float


class CalculateResponse(BaseModel):
    """Full response from the /calculate endpoint."""

    margin_capital: float
    project_cost: float
    loan_amount: float
    scheme: Optional[SchemeInfo]
    emi: Optional[EMIInfo]
    repayment_schedule: list[RepaymentEntryResponse]
    quarterly_summary: list[QuarterlySummaryResponse]
    scheme_limit_warning: Optional[str]
    disclaimer: str


# ---- Endpoints ----


@app.get("/schemes", response_model=list[SchemeInfo])
async def list_schemes():
    """List all available financing schemes."""
    return [
        SchemeInfo(
            name=s.name,
            description=s.description,
            max_project_cost=s.max_project_cost,
            max_loan_amount=s.max_loan_amount,
            interest_rate_annual=s.interest_rate_annual,
            tenure_years=s.tenure_years,
            moratorium_months=s.moratorium_months,
        )
        for s in SCHEMES
    ]


@app.post("/calculate", response_model=CalculateResponse)
async def calculate(request: CalculateRequest):
    """Full financial calculation from margin capital input."""
    # Validate
    validation = validate_margin(str(request.margin_capital))
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.error_message)

    margin = validation.value
    project_cost = calculate_project_cost(margin)
    scheme = select_scheme(project_cost)
    limit_result = check_scheme_limits(project_cost)

    loan_amount = 0.0
    emi_info = None
    scheme_info = None
    schedule = []
    quarterly = []

    if scheme:
        loan_amount = calculate_loan_amount(project_cost, scheme)
        emi_result = calculate_emi(loan_amount, scheme)
        emi_info = EMIInfo(
            monthly_emi=emi_result.monthly_emi,
            total_repayment=emi_result.total_repayment,
            total_interest=emi_result.total_interest,
            total_months=emi_result.total_months,
            moratorium_months=emi_result.moratorium_months,
        )
        scheme_info = SchemeInfo(
            name=scheme.name,
            description=scheme.description,
            max_project_cost=scheme.max_project_cost,
            max_loan_amount=scheme.max_loan_amount,
            interest_rate_annual=scheme.interest_rate_annual,
            tenure_years=scheme.tenure_years,
            moratorium_months=scheme.moratorium_months,
        )
        raw_schedule = generate_repayment_schedule(loan_amount, scheme)
        schedule = [
            RepaymentEntryResponse(
                month=e.month,
                opening_balance=e.opening_balance,
                emi_amount=e.emi_amount,
                principal_component=e.principal_component,
                interest_component=e.interest_component,
                closing_balance=e.closing_balance,
            )
            for e in raw_schedule
        ]
        quarterly = [
            QuarterlySummaryResponse(
                quarter=q.quarter,
                start_month=q.start_month,
                end_month=q.end_month,
                principal_paid=q.principal_paid,
                interest_paid=q.interest_paid,
                total_payment=q.total_payment,
                remaining_loan=q.remaining_loan,
            )
            for q in generate_quarterly_summary(raw_schedule)
        ]

    return CalculateResponse(
        margin_capital=margin,
        project_cost=project_cost,
        loan_amount=loan_amount,
        scheme=scheme_info,
        emi=emi_info,
        repayment_schedule=schedule,
        quarterly_summary=quarterly,
        scheme_limit_warning=limit_result.warning_message,
        disclaimer=(
            "Figures are based on the SIH problem-statement assumptions "
            "and are for advisory/illustrative purposes. Actual eligibility "
            "and repayment terms must be verified against the latest official "
            "scheme guidelines."
        ),
    )
