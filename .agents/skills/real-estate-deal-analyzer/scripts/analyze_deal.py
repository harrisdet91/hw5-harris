#!/usr/bin/env python3
"""
Analyze a rental real estate deal using deterministic financial formulas.

Usage:
  python scripts/analyze_deal.py --input deal.json
  python scripts/analyze_deal.py --json '{"purchase_price": 575000, "monthly_rent": 2895, ...}'

The script prints JSON to stdout.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Any, Dict


REQUIRED_FIELDS = [
    "purchase_price",
    "monthly_rent",
    "down_payment_percent",
    "annual_interest_rate_percent",
    "loan_term_years",
]


OPTIONAL_DEFAULTS = {
    "annual_property_taxes": 0.0,
    "annual_insurance": 0.0,
    "monthly_hoa": 0.0,
    "monthly_repairs_maintenance": 0.0,
    "monthly_vacancy_reserve": 0.0,
    "monthly_property_management": 0.0,
    "other_monthly_expenses": 0.0,
    "closing_costs": 0.0,
    "upfront_repairs": 0.0,
}


def _as_float(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be numeric.")
    if math.isnan(number) or math.isinf(number):
        raise ValueError(f"{field} must be a finite number.")
    return number


def validate_inputs(data: Dict[str, Any]) -> Dict[str, float]:
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")

    merged = dict(OPTIONAL_DEFAULTS)
    merged.update(data)

    clean: Dict[str, float] = {}
    for field, value in merged.items():
        clean[field] = _as_float(value, field)

    if clean["purchase_price"] <= 0:
        raise ValueError("purchase_price must be greater than 0.")
    if clean["monthly_rent"] < 0:
        raise ValueError("monthly_rent cannot be negative.")
    if not 0 <= clean["down_payment_percent"] <= 100:
        raise ValueError("down_payment_percent must be between 0 and 100.")
    if clean["annual_interest_rate_percent"] < 0:
        raise ValueError("annual_interest_rate_percent cannot be negative.")
    if clean["loan_term_years"] <= 0:
        raise ValueError("loan_term_years must be greater than 0.")

    for field in OPTIONAL_DEFAULTS:
        if clean[field] < 0:
            raise ValueError(f"{field} cannot be negative.")

    return clean


def monthly_mortgage_payment(loan_amount: float, annual_rate_percent: float, years: float) -> float:
    if loan_amount <= 0:
        return 0.0

    months = int(round(years * 12))
    monthly_rate = annual_rate_percent / 100 / 12

    if monthly_rate == 0:
        return loan_amount / months

    return loan_amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)


def analyze_deal(data: Dict[str, Any]) -> Dict[str, Any]:
    x = validate_inputs(data)

    purchase_price = x["purchase_price"]
    monthly_rent = x["monthly_rent"]
    down_payment = purchase_price * (x["down_payment_percent"] / 100)
    loan_amount = purchase_price - down_payment

    monthly_pi = monthly_mortgage_payment(
        loan_amount=loan_amount,
        annual_rate_percent=x["annual_interest_rate_percent"],
        years=x["loan_term_years"],
    )

    monthly_taxes = x["annual_property_taxes"] / 12
    monthly_insurance = x["annual_insurance"] / 12

    monthly_operating_expenses = (
        monthly_taxes
        + monthly_insurance
        + x["monthly_hoa"]
        + x["monthly_repairs_maintenance"]
        + x["monthly_vacancy_reserve"]
        + x["monthly_property_management"]
        + x["other_monthly_expenses"]
    )

    monthly_noi = monthly_rent - monthly_operating_expenses
    annual_noi = monthly_noi * 12
    monthly_cash_flow = monthly_noi - monthly_pi
    annual_cash_flow = monthly_cash_flow * 12
    annual_debt_service = monthly_pi * 12

    cap_rate = annual_noi / purchase_price if purchase_price else None
    dscr = annual_noi / annual_debt_service if annual_debt_service else None

    initial_cash_invested = down_payment + x["closing_costs"] + x["upfront_repairs"]
    cash_on_cash_return = annual_cash_flow / initial_cash_invested if initial_cash_invested else None

    def money(v: float) -> float:
        return round(v, 2)

    def pct(v: float | None) -> float | None:
        return None if v is None else round(v * 100, 2)

    def ratio(v: float | None) -> float | None:
        return None if v is None else round(v, 2)

    return {
        "inputs": x,
        "results": {
            "purchase_price": money(purchase_price),
            "down_payment": money(down_payment),
            "loan_amount": money(loan_amount),
            "monthly_rent": money(monthly_rent),
            "monthly_principal_and_interest": money(monthly_pi),
            "monthly_operating_expenses": money(monthly_operating_expenses),
            "monthly_noi": money(monthly_noi),
            "monthly_cash_flow_after_debt_service": money(monthly_cash_flow),
            "annual_noi": money(annual_noi),
            "annual_cash_flow_after_debt_service": money(annual_cash_flow),
            "cap_rate_percent": pct(cap_rate),
            "dscr": ratio(dscr),
            "initial_cash_invested": money(initial_cash_invested),
            "cash_on_cash_return_percent": pct(cash_on_cash_return),
        },
        "interpretation_flags": build_flags(monthly_cash_flow, dscr, cap_rate, cash_on_cash_return),
    }


def build_flags(monthly_cash_flow: float, dscr: float | None, cap_rate: float | None, coc: float | None) -> list[str]:
    flags: list[str] = []

    if monthly_cash_flow < 0:
        flags.append("Negative monthly cash flow after debt service.")
    elif monthly_cash_flow < 200:
        flags.append("Thin positive cash flow; small expense changes could erase it.")
    else:
        flags.append("Positive monthly cash flow after debt service.")

    if dscr is not None:
        if dscr < 1:
            flags.append("DSCR below 1.00 means NOI does not cover debt service.")
        elif dscr < 1.20:
            flags.append("DSCR is positive but thin.")
        else:
            flags.append("DSCR appears healthy under the provided assumptions.")

    if cap_rate is not None and cap_rate < 0.04:
        flags.append("Cap rate is low; the deal may depend heavily on appreciation or tax benefits.")

    if coc is not None and coc < 0:
        flags.append("Cash-on-cash return is negative under the provided assumptions.")

    return flags


def load_input(args: argparse.Namespace) -> Dict[str, Any]:
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            return json.load(f)
    if args.json:
        return json.loads(args.json)
    raise ValueError("Provide either --input path/to/file.json or --json '{...}'.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a rental real estate deal.")
    parser.add_argument("--input", help="Path to a JSON input file.")
    parser.add_argument("--json", help="Inline JSON string.")
    args = parser.parse_args()

    try:
        data = load_input(args)
        result = analyze_deal(data)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
