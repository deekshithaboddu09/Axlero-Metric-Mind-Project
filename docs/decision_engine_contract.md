# Decision Engine Contract

**Status: Proposed — Pending Deekshitha's Approval**

## Purpose

Define the proposed inputs, outputs, and validation behaviour for the initial shipment Decision Engine.

## Proposed Input Fields

| Field | Meaning | Proposed validation |
|---|---|---|
| `shipment_id` | Unique shipment identifier | Required; not blank |
| `origin` | Shipment starting location | Required |
| `destination` | Shipment delivery location | Required |
| `estimated_delivery_date` | Expected delivery date | Required; date rules need approval |
| `shipping_cost` | Known shipping cost | Non-negative number; currency needs approval |
| `risk_indicator` | Available indication of shipment risk | Accepted values need approval |

## Proposed Output Fields

| Field | Meaning |
|---|---|
| `option_name` | Name of a potential shipping option |
| `estimated_cost` | Estimated cost if supported by available data |
| `risk_note` | Known risks or missing risk information |
| `explanation` | Plain-English explanation of the result |

## Proposed Validation Behaviour

- Identify missing required information.
- Flag invalid inputs according to approved rules.
- Do not treat missing cost or risk information as zero.
- Do not invent options, costs, or delivery dates.
- If suitability cannot be established, explain why.

## Pending Decisions

- First-version decision scope.
- Required fields and accepted risk values.
- Cost calculation and comparison rules.
- Handling of missing information.
- Criteria for determining whether an option is suitable.

All fields and rules are proposals, not finalized requirements.

**Approval status:** Pending Deekshitha's review.
