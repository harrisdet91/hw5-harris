# HW5 — Real Estate Deal Analyzer Skill

Video link: `ADD YOUR VIDEO LINK HERE`

## What the skill does

`real-estate-deal-analyzer` is a reusable AI skill for evaluating rental-property investment scenarios. It calculates exact financial metrics including:

- monthly mortgage principal and interest
- monthly operating expenses
- monthly NOI
- monthly cash flow after debt service
- cap rate
- DSCR
- cash-on-cash return

## Why I chose it

I chose this skill because real estate deal analysis combines judgment with deterministic financial math. A language model can explain the result and organize the workflow, but it should not be trusted to consistently calculate mortgage payments, DSCR, cap rate, or cash-on-cash return by hand.

The Python script is therefore load-bearing: it performs the exact calculations, while the skill instructions tell the agent when to use the script and how to explain the output.

## How to use it

Place the skill folder in:

```text
.agents/skills/real-estate-deal-analyzer/
```

Then ask an agent in a supported coding environment, such as Codex, VS Code Copilot Agent, or Claude Code:

```text
Analyze this rental property deal:
purchase price $575,000
rent $2,895/month
10% down
5.875% interest
30-year loan
taxes $12,000/year
insurance $1,000/year
HOA $450/month
maintenance $200/month
vacancy reserve $145/month
```

The agent should activate the skill, run the Python script, and summarize the result.

## What the script does

The script is located at:

```text
.agents/skills/real-estate-deal-analyzer/scripts/analyze_deal.py
```

It accepts either a JSON file or inline JSON and returns structured JSON output.

Example:

```bash
python .agents/skills/real-estate-deal-analyzer/scripts/analyze_deal.py \
  --input examples/normal_case.json
```

## Test prompts

### 1. Normal case

```text
Analyze this rental property deal using the real estate deal analyzer:
purchase price $575,000, monthly rent $2,895, 10% down, 5.875% interest, 30-year term,
annual taxes $12,000, annual insurance $1,000, HOA $450/month, maintenance $200/month,
vacancy reserve $145/month, no property management, closing costs $10,000.
```

Expected behavior: the agent should run the script and produce a full deal summary.

### 2. Edge case

```text
Analyze this deal where monthly rent is $0, purchase price is $575,000, interest rate is 9.5%,
10% down, 30-year loan, annual taxes $12,000, annual insurance $1,000, HOA $450/month.
```

Expected behavior: the script should still run and show strongly negative cash flow and weak DSCR.

### 3. Cautious / limited case

```text
Analyze this rental property: purchase price $575,000 and rent $2,895/month.
```

Expected behavior: the agent should not invent missing assumptions. It should ask for missing inputs such as interest rate, down payment, loan term, taxes, insurance, and expenses.

## What worked well

The skill creates a clear division of labor:

- the skill file provides activation logic, guardrails, and output format
- the Python script performs repeatable calculations
- the agent interprets the results for the user

This follows the idea that skills should be reusable task playbooks, while scripts handle deterministic work.

## Limitations

This skill does not automatically verify rent, taxes, insurance, vacancy rates, maintenance, appreciation, or financing terms. It is a financial modeling aid, not legal, tax, lending, or investment advice.

The output is only as reliable as the assumptions provided by the user.
