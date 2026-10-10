# Payslip layout notes

## Status and handoff

- Format-neutral content and hierarchy notes, based on the provisionally approved wireframe.
- Not a final fillable template or a populated payslip.
- Final template format, required fields, sizing, page breaks and exact styling await Law's confirmation and Damian's review.
- Priority handoff: before 18:00, after Law confirms the format. These notes can be reviewed now; do not mark the final template as delivered.
- All business values and run-dependent text remain named placeholders. Placeholder names below are display slots, not new ledger columns or an agreed output schema.

## Approved visual hierarchy

- One continuous document; do not turn every section into an equally prominent card.
- Warm, student-first language with clear section headings and generous separation between major groups.
- Week and dates provide context; the hourly rate is the dominant element.
- Take home and total time are secondary; supporting breakdowns are quieter but readable.
- Decisions follow the financial evidence. Keep review items last, with a distinct heading and border so they are easy to find.
- Do not rely on colour alone for warnings or authority. Exact colours and typography remain pending.

## Fixed top-to-bottom order

### 1. Week and date range

- Heading: “Lembur · Weekly payslip”.
- Context: `{week}` · `{date_range}`.
- Use the verified Monday-to-Sunday reporting week and Malaysia-time dates.
- Keep this smaller than the hourly-rate headline.

### 2. Hourly rate — the headline

- Heading: “What your time earned”.
- Primary value: “RM {hourly_rate} per hour”.
- Supporting wording: “Based on recorded earnings and estimated working time, with stated event time included.”
- Keep the assumption-based nature of hours visible; do not call them tracked or measured hours.
- When an expense amount is unreadable or missing, place this caveat immediately below the headline: “Provisional earnings: an expense amount is unknown. Your take home and hourly rate may be lower once it is confirmed.”
- Do not display an hourly-rate value when the week has no minutes; do not invent a replacement rate.

### 3. Take home, with totals by category

- Heading: “What you took home”.
- Secondary value: “RM {take_home}”.
- Breakdown, in point form:
  - Sales: “RM {sales_total}”.
  - Materials: “RM {materials_total}”.
  - Packaging: “RM {packaging_total}”.
  - Fees: “RM {platform_fees_total}”.
  - Shipping: “RM {shipping_total}”.
  - Other expenses: “RM {other_expenses_total}”.
- Map the human-facing label “Fees” to the existing `platform_fees` category; do not create a new category.
- Copy all values from the numbers tool. Take home uses counted ledger income and expenses, not the sum of product profits.
- If an expense amount is unknown, retain the provisional-earnings caveat near take home; never display the unknown amount as zero.

### 4. Hours by activity, with the total

- Heading: “Where your time went”.
- Production: “{production_hours} hours”.
- Fulfilment: “{fulfilment_hours} hours”.
- Events: “{event_hours} hours”.
- Admin: “{admin_hours} hours”.
- Emphasised total: “{total_hours} hours”.
- Production, fulfilment and admin use plan assumptions or dated corrections; events use clear durations stated in saved messages.
- Show `{hours_source_note}` with verified source references where needed; do not invent a correction history.
- Keep total hours visually distinct from the activity breakdown, but smaller than the hourly-rate headline.

### 5. Shared hours

- Heading: “Time shared across your business”.
- Line: “Events + admin: {shared_hours} hours”.
- Explanation: “Already included in total time; not assigned to individual products.”
- Do not add shared hours again or allocate them arbitrarily across products.

### 6. Profit per hour by product

- Heading: “What each product pays per hour”.
- Repeat one point-form group per verified product:
  - `{product_name}`: “RM {product_profit_per_hour} per direct hour”.
  - Supporting product profit: “RM {product_profit}”.
  - `{product_loss_marker}`: display the explicit label “Loses money” only when the tool result says product profit is below zero.
- Explanation: “Product rates use production and fulfilment time only. Shared event and admin time is excluded.”
- Explanation: “Product profit uses plan costs; take home uses ledger payments. Product profits do not add up to take home.”
- Do not confuse a product's direct hourly profit with the whole-business hourly rate.

### 7. Plan versus reality

- Heading: “Your plan versus this week”.
- Hourly rate: “RM {target_hourly_rate} target → RM {hourly_rate} actual”.
- Margin: “{planned_margin_percent}% planned → {actual_margin_percent}% actual”.
- Keep hourly earnings visually ahead of the supporting margin comparison.
- Use the plan's target for the hourly-rate comparison; do not relabel it as a generated Day Zero prediction.
- Do not display the actual margin when sales are zero.
- Retain the provisional label on current earnings when an expense amount is unknown.

### 8. Debate summary and Auditor's ruling

- Heading: “The debate and the ruling”.
- Payroll: `{payroll_recommendation_summary}` · `{payroll_cited_evidence}`.
- Growth coach: `{growth_recommendation_summary}` · `{growth_cited_evidence}`.
- Auditor: `{upheld_side_and_change}` · `{ruling_reason_with_citations}`.
- Distinguish recommendations from the ruling through labels and spacing.
- Populate only from the actual recommendation and ruling files. An expected ruling direction in the answer key is not an observed ruling.
- Use `submission/board_meeting_layout.md` for the expanded disagreement presentation.

### 9. Raise plan, linked to drafts

- Heading: “Your raise plan”.
- Repeat one group per recommendation upheld by the actual ruling:
  - `{upheld_recommendation}`.
  - Draft to review: `{draft_reference}` in `approvals/{week}/`.
  - State: “Waiting for individual approval”.
- No projected hourly raise or guaranteed improvement while the projection rules remain unconfirmed.
- Do not insert a generic approval button or imply approval handling is implemented. The supported interaction must be confirmed by Law.
- Nothing is sent or posted before the student approves that draft individually.

### 10. Needs-your-review list

- Heading: “Needs your review”.
- Keep this section last; use a distinct boundary and clear wording rather than moving it above the financial sections.
- Repeat one group per actual review item:
  - `{review_reference}` · `{review_status}`.
  - `{review_reason}`.
  - `{source_reference}`.
  - `{requested_clarification}`.
- Include every row with `unmatched`, `duplicate` or `needs_review` status, plus applicable hours-review items; use the Auditor's final review list.
- For an unreadable expense, ask for a clearer source and keep the amount unknown. For a bank-only row, do not invent a receipt link.
- Do not suppress a review item because a known amount is already counted in totals.

## Population and verification rules

- Retain placeholders until verified run outputs or Sharon's approved, independently checked answer key supply the values. Final run evidence must still be checked against that key.
- The currently merged answer key is an independently verified draft awaiting Sharon's business sign-off; it is not an approved release or proof of an end-to-end run.
- Copy calculated values; do not calculate totals, convert time or project earnings inside these layout notes.
- Apply the documented display conventions through the established calculation/output process: ringgit with two decimal places, hours with one, percentages whole, halves away from zero.
- Empty means unknown or not applicable, not a numeric zero. Keep legitimate calculated zero values distinct from missing evidence.
- Preserve source references, unknown-expense caveats and review coverage when adapting the notes to Law's confirmed template format.
- Demo data only; no private documents, credentials or authoring credits.

## Sources

- Human-language design principle: `docs/PLAN.md`, section 2.
- Scope and validation: `docs/PLAN.md`, sections 4 and 10.
- Display conventions, hours and financial bases: `docs/SYSTEM_DESIGN.md`, sections 2, 4.2 and 4.3.
- Agent authority, individual approval and fixed output order: `docs/SYSTEM_DESIGN.md`, sections 5, 6.1 and 7.
- Unconfirmed projections: `docs/SYSTEM_DESIGN.md`, section 8.
- Current fixture status and unknown-expense limitation: `data/answer_key/answer_key.md`, “Validation and limitations”; fixture evidence does not replace the source-of-truth docs.
- Visual hierarchy: Damian's provisional approval of the format-neutral wireframe.
