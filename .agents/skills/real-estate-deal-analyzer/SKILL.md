---
name: real-estate-deal-analyzer
description: Calculates rental-property investment metrics including mortgage payment, NOI, cap rate, DSCR, cash-on-cash return, and monthly cash flow. Use when a user asks to evaluate, compare, or sanity-check a rental property deal using exact financial inputs.
---

# Real Estate Deal Analyzer

## When to use this skill

Use this skill when the user wants to evaluate a rental property or compare real estate investment scenarios using specific numeric assumptions.

Good requests include:
- "Analyze this rental deal."
- "Calculate cash flow and DSCR for this property."
- "Compare these two rental scenarios."
- "Is this property cash-flow positive?"
- "What is the cap rate and cash-on-cash return?"

## When not to use this skill

Do not use this skill for:
- predicting appreciation
- giving legal, tax, or lending advice
- estimating current market rents without user-provided data
- making a buy/sell recommendation without noting uncertainty
- analyzing a deal when required numeric inputs are missing

If key inputs are missing, ask for them instead of inventing values.

## Expected inputs

The user should provide most or all of the following:

- purchase price
- monthly rent
- down payment percentage
- annual interest rate
- loan term in years
- annual property taxes
- annual insurance
- monthly HOA dues
- monthly repairs/maintenance reserve
- monthly vacancy reserve
- monthly property management cost
- other monthly expenses

## Deterministic script

For all calculations, use:

`scripts/analyze_deal.py`

The script performs the deterministic financial calculations. Do not calculate these metrics by hand in prose unless the script cannot run.

The script expects a JSON file or inline JSON object with the deal assumptions. It returns JSON containing:

- loan amount
- monthly principal and interest payment
- monthly operating expenses
- monthly net operating income
- monthly cash flow after debt service
- annual NOI
- cap rate
- debt service coverage ratio
- initial cash invested
- cash-on-cash return

## Workflow

1. Parse the user's assumptions into the script input schema.
2. If important values are missing, ask for them instead of guessing.
3. Run `scripts/analyze_deal.py` with the assumptions.
4. Read the JSON output from the script.
5. Present the final answer in plain English.
6. Clearly label assumptions.
7. Include a short interpretation of the result, but do not overstate certainty.

## Output format

Use this structure:

### Deal Summary
Briefly state whether the property appears cash-flow positive or negative under the provided assumptions.

### Key Metrics
Provide:
- Monthly rent
- Monthly P&I payment
- Monthly operating expenses
- Monthly NOI
- Monthly cash flow after debt service
- Cap rate
- DSCR
- Cash-on-cash return

### Interpretation
Explain what the numbers mean. Mention any weak spots, such as low DSCR, negative cash flow, high HOA dues, or reliance on appreciation.

### Missing or uncertain items
List any assumptions that were missing, estimated, or especially important.

## Important limitations

This skill provides a deterministic financial model, not professional financial, legal, tax, or lending advice.

The output is only as reliable as the user's inputs. It does not automatically verify market rent, property taxes, insurance, repair costs, appreciation, or vacancy risk.
