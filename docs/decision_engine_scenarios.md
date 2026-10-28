# Decision Engine Scenarios

**Status: Mock Scenarios — Pending Approval**

All values below are illustrative, not real shipment data.

## Scenario 1: Normal Shipment

**Inputs**
- Shipment ID: `SH-001`
- Origin: Pune
- Destination: Mumbai
- Estimated delivery date: `2026-11-02`
- Shipping cost: `500` (currency pending approval)
- Risk indicator: `Low` (example value)

**Expected behaviour**

Validate the available fields. If approved options and evaluation rules exist, return the eligible result with an explanation. Do not claim that an option is best or cheapest without approved comparison rules.

## Scenario 2: Delayed Shipment

**Inputs**
- Shipment ID: `SH-002`
- Origin: Pune
- Destination: Delhi
- Estimated delivery date: `2026-10-25`
- Shipping cost: `800`
- Risk indicator: `High`

**Expected behaviour**

Validate the date and risk information. A past estimated date alone does not prove that the shipment is delayed. Check actual shipment status and the reference date before identifying a delay. Do not invent a revised date.

## Scenario 3: High-Cost Option

**Inputs**
- Shipment ID: `SH-003`
- Origin: Pune
- Destination: Bengaluru
- Estimated delivery date: `2026-11-04`
- Shipping cost: `2500`
- Risk indicator: `Medium`

**Expected behaviour**

Validate the cost and required fields. Present a cost comparison only if comparable options and approved rules are available. Do not claim savings or identify the cheapest option without supporting data.

## Scenario 4: Missing Required Field

**Inputs**
- Shipment ID: `SH-004`
- Origin: Pune
- Destination: Missing
- Estimated delivery date: `2026-11-03`
- Shipping cost: `600`
- Risk indicator: `Low`

**Expected behaviour**

If destination is approved as a required field, identify it as missing and explain that the input is incomplete. Request the missing information or return an approved validation message. Do not invent a destination.

## Scenario 5: No Suitable Option

**Inputs**
- Shipment ID: `SH-005`
- Origin: Pune
- Destination: London
- Estimated delivery date: `2026-11-01`
- Shipping cost: `1500`
- Risk indicator: `High`

**Expected behaviour**

Evaluate suitability only against available options and approved rules. If no option meets those rules, explain that no suitable option is available. If option data or rules are missing, state that a decision cannot yet be established. Do not invent an option.

## Review Notes

- All inputs are mock values.
- Required fields and risk values need approval.
- No savings, business formulas, or final recommendations are claimed.
- Implementation should follow agreement on the contract and decision scope.
