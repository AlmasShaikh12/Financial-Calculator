# SIH Financial Calculator — Reliable Financial Calculator & Scheme Router

> **Phase 1** of the SIH Financing Prototype. This module provides a completely reliable, deterministic financial calculation core with no AI/LLM involvement in any computation.

---

## ⚠️ Disclaimer

All scheme parameters and calculations are **based on the SIH problem statement** and are for advisory/illustrative purposes only. Actual eligibility and repayment terms **must be verified against the latest official scheme guidelines**. This calculator does **not** guarantee loan eligibility.

---

## 🏗 Architecture

```
sih-finance-calculator/
├── backend/
│   ├── financial_engine/          # Python financial engine (for FastAPI)
│   │   ├── __init__.py            # Package exports
│   │   ├── schemes.py             # Scheme configuration & parameters
│   │   ├── calculations.py        # Project cost, loan amount, margin
│   │   ├── emi.py                 # EMI calculation (reducing-balance)
│   │   ├── repayment.py           # Monthly & quarterly repayment schedules
│   │   └── validation.py          # Input validation & scheme limit checking
│   ├── tests/
│   │   └── test_calculations.py   # 55 comprehensive tests
│   ├── api.py                     # FastAPI stub (ready for integration)
│   ├── requirements.txt
│   └── run_tests.py               # Test runner
│
├── frontend/
│   ├── index.html                 # Standalone calculator UI (zero dependencies)
│   └── src/utils/                 # TypeScript financial engine (React-ready)
│       ├── schemes.ts
│       ├── calculations.ts
│       ├── emi.ts
│       ├── repayment.ts
│       ├── validation.ts
│       ├── formatters.ts
│       └── index.ts
│
└── README.md
```

### Design Principles

- **Deterministic**: All calculations use programmed math — no AI/LLM for computation
- **Configurable**: Scheme parameters are defined in one place, not hard-coded
- **Separate concerns**: Financial logic is completely separate from UI
- **Dual implementation**: Python (for FastAPI) + TypeScript (for React) with identical logic
- **Testable**: 55 automated tests covering all boundaries and edge cases

---

## 💰 Scheme Parameters

| Parameter | Micro Finance | Term Loan |
|-----------|--------------|-----------|
| Project cost range | Up to ₹1,40,000 | ₹1,40,001 – ₹50,00,000 |
| Funding % | 90% | 90% |
| Maximum loan | ₹1,25,000 | ₹45,00,000 |
| Interest rate | 6.5% p.a. | 8% p.a. |
| Tenure | 3 years | 7 years |
| Moratorium | 3 months | 6 months |

---

## 🚀 Quick Start

### Open the Calculator (Frontend)

Simply open `frontend/index.html` in any web browser. No build tools or dependencies required.

### Run the Backend Tests

```bash
cd backend
pip install pytest
python -m pytest tests/test_calculations.py -v
```

### Start the FastAPI Server

```bash
cd backend
pip install fastapi uvicorn
uvicorn api:app --reload
```

Then visit `http://localhost:8000/docs` for the interactive API docs.

---

## 🔬 Financial Formulas

### Project Cost
```
Project Cost = Available Margin Capital / 0.10
```

### Loan Amount
```
Loan = Project Cost × 0.90  (capped at scheme maximum)
```

### EMI (Reducing Balance)
```
EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)

Where:
  P = Loan principal
  r = Monthly interest rate (annual / 12)
  n = Total monthly installments (years × 12)
```

---

## ✅ Test Coverage

**55 tests** covering:

| Category | Tests | Covers |
|----------|-------|--------|
| Input Validation | 13 | Empty, zero, negative, text, commas, ₹ symbol |
| Scheme Selection | 9 | Both schemes, ₹1.40L boundary, ₹50L boundary, beyond limits |
| Core Calculations | 4 | Project cost formula, margin reverse calculation |
| Loan Amount | 6 | Standard, capped, micro finance, negative input |
| Scheme Parameters | 3 | Verify all SIH problem statement values |
| EMI Calculation | 5 | Standard formula, boundary, error handling |
| Repayment Schedule | 11 | Monthly, quarterly, monotonic decrease, totals |
| End-to-End | 4 | Full pipeline for ₹1L, ₹6L(exceeds), ₹14K(boundary), ₹5L(boundary) |

---

## 📋 Key Test Cases

| # | Input | Project Cost | Loan | Scheme |
|---|-------|-------------|------|--------|
| 1 | ₹10,000 | ₹1,00,000 | ₹90,000 | Micro Finance |
| 2 | ₹14,000 | ₹1,40,000 | ₹1,25,000 (capped) | Micro Finance |
| 3 | ₹14,001 | ₹1,40,010 | ₹1,26,009 | Term Loan |
| 4 | ₹15,000 | ₹1,50,000 | ₹1,35,000 | Term Loan |
| 5 | ₹1,00,000 | ₹10,00,000 | ₹9,00,000 | Term Loan |
| 6 | ₹5,00,000 | ₹50,00,000 | ₹45,00,000 | Term Loan (max) |
| 7 | ₹5,00,001 | ₹50,00,010 | ⚠ Warning | None |

---

## 🔌 API Endpoints (FastAPI Stub)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/schemes` | List all available schemes |
| `POST` | `/calculate` | Full calculation from margin capital |

### Example Request

```json
POST /calculate
{
  "margin_capital": 100000
}
```

### Example Response

```json
{
  "margin_capital": 100000,
  "project_cost": 1000000,
  "loan_amount": 900000,
  "scheme": {
    "name": "Term Loan Scheme",
    "interest_rate_annual": 0.08,
    "tenure_years": 7,
    "moratorium_months": 6
  },
  "emi": {
    "monthly_emi": 14027.59,
    "total_repayment": 1178317.81,
    "total_interest": 278317.81
  },
  "disclaimer": "Figures are based on the SIH problem-statement assumptions..."
}
```

---

## 🗺 Roadmap

- [ ] Phase 2: FastAPI + React integration
- [ ] Phase 3: Database persistence (scheme rules, user sessions)
- [ ] Phase 4: AI assistant (RAG for scheme documentation)
- [ ] Phase 5: Market analysis & competitor modules

---

## 📄 License

This project was built for the Smart India Hackathon (SIH).
