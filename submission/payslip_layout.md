# Payslip layout notes

For fields and placeholders this note is superseded by submission/payslip_template.html once that file exists. Until then it lists the placeholders the template must use.

## Status and handoff

- Content and hierarchy notes, based on the provisionally approved wireframe.
- Not a populated payslip.
- Format is decided (design section 7): an HTML template at `submission/payslip_template.html`, filled by a script from `audit/<week>/numbers.json`. A PDF is wanted and waits on check 11. Fallback: the HTML file is the payslip.
- Due 18:00 as `submission/payslip_template.html`. Sizing, page breaks and exact styling await Damian's review.
- Placeholders use `{{name}}` with the field names in design section 7. No field may be added without asking Law.

## Approved visual hierarchy

- One continuous document; do not turn every section into an equally prominent card.
- Warm, student first language with clear section headings and generous separation between major groups.
- Week and dates provide context; the hourly rate is the dominant element.
- Take home and total time are secondary; supporting breakdowns are quieter but readable.
- Decisions follow the financial evidence. Keep review items last, with a distinct heading and border so they are easy to find.
- Do not rely on colour alone for warnings or authority. Exact colours and typography remain pending.

## Fixed top to bottom order

### 1. Week and date range

- Heading: “Lembur · Weekly payslip”.
- Context: `{{week}}` · `{{date_from}}` to `{{date_to}}`.
- Use the verified Monday to Sunday reporting week and Malaysia time dates.
- Keep this smaller than the hourly rate headline.

### 2. Hourly rate, the headline

- Heading: “What your time earned”.
- Primary value: “RM {{hourly_rate_rm}} per hour”.
- Supporting wording: “Based on recorded earnings and estimated working time, with stated event time included.”
- Keep the assumption based nature of hours visible; do not call them tracked or measured hours.
- Static line immediately below the headline: “The rate uses the amounts we could read. Anything unreadable is listed under Needs your review.”
- Do not invent a replacement rate when the week has no minutes; the placeholder is filled with nothing.

### 3. Take home, with totals by category

- Heading: “What you took home”.
- Secondary value: “RM {{take_home_rm}}”.
- Breakdown, in point form:
  - Sales: “RM {{category_totals_rm.sales}}”.
  - Materials: “RM {{category_totals_rm.materials}}”.
  - Packaging: “RM {{category_totals_rm.packaging}}”.
  - Fees: “RM {{category_totals_rm.platform_fees}}”.
  - Shipping: “RM {{category_totals_rm.shipping}}”.
  - Other expenses: “RM {{category_totals_rm.other_expenses}}”.
- Map the human facing label “Fees” to the existing `platform_fees` category; do not create a new category.
- Copy all values from the numbers tool. Take home uses counted ledger income and expenses, not the sum of product profits.
- Keep the static line from section 2 near take home; never display an unknown amount as zero.

### 4. Hours by activity, with the total

- Heading: “Where your time went”.
- Production: “{{hours.production}} hours”.
- Fulfilment: “{{hours.fulfilment}} hours”.
- Events: “{{hours.event}} hours”.
- Admin: “{{hours.admin}} hours”.
- Emphasised total: “{{hours.total}} hours”.
- Production, fulfilment and admin use plan assumptions or dated corrections; events use clear durations stated in saved messages.
- Keep total hours visually distinct from the activity breakdown, but smaller than the hourly rate headline.

### 5. Shared hours

- Heading: “Time shared across your business”.
- Line: “Events + admin: {{shared_hours}} hours”.
- Explanation: “Already included in total time; not assigned to individual products.”
- Do not add shared hours again or allocate them arbitrarily across products.

### 6. Profit per hour by product

- Heading: “What each product pays per hour”.
- Repeat one point form group per product, between `<!-- each products -->` and `<!-- end products -->`:
  - `{{name}}`: “RM {{profit_per_hour_rm}} per direct hour”.
  - Supporting product profit: “RM {{profit_rm}}”.
  - `{{loses_money}}`: filled as `true` or `false` to drive a style class. The label “Loses money” is static text in the block, shown only by that class.
- Explanation: “Product rates use production and fulfilment time only. Shared event and admin time is excluded.”
- Explanation: “Product profit uses plan costs; take home uses ledger payments. Product profits do not add up to take home.”
- Do not confuse a product's direct hourly profit with the whole business hourly rate.

### 7. Plan versus reality

- Heading: “Your plan versus this week”.
- Hourly rate: “RM {{plan_versus_reality.target_hourly_rate_rm}} target → RM {{plan_versus_reality.hourly_rate_rm}} actual”.
- Margin: “{{plan_versus_reality.planned_margin_percent}}% planned → {{plan_versus_reality.margin_percent}}% actual”.
- Keep hourly earnings visually ahead of the supporting margin comparison.
- Use the plan's target for the hourly rate comparison; do not relabel it as a generated Day Zero prediction.
- Do not display the actual margin when sales are zero.
- Keep the static line from section 2 near current earnings.

### 8. Debate summary and Auditor's ruling

- Heading: “The debate and the ruling”.
- Debate summary: `{{debate_summary}}`.
- Auditor's ruling: `{{ruling}}`.
- Both are copied from `boardroom/<week>/ruling.md`.
- Distinguish recommendations from the ruling through labels and spacing.
- Populate only from the actual recommendation and ruling files. An expected ruling direction in the answer key is not an observed ruling.
- Use `submission/board_meeting_layout.md` for the expanded disagreement presentation.

### 9. Raise plan, linked to drafts

- Heading: “Your raise plan”.
- Repeat one group per recommendation upheld by the actual ruling, between `<!-- each raise_plan -->` and `<!-- end raise_plan -->`:
  - `{{text}}`.
  - Draft to review: `{{draft_file}}` in `approvals/<week>/`.
  - Under each draft: reply “approve N” to approve it or “skip N” to leave it. No button.
- No projected hourly raise or guaranteed improvement: the raise projection is an agreed design, not built.
- Lembur posts and sends nothing. The student sends an approved draft herself.

### 10. Needs your review list

- Heading: “Needs your review”.
- Keep this section last; use a distinct boundary and clear wording rather than moving it above the financial sections.
- Transaction rows, one group per row, between `<!-- each review_rows -->` and `<!-- end review_rows -->`:
  - `{{txn_id}}` · `{{reconciliation_status}}` · `{{date}}`.
  - `{{amount_rm}}` · `{{description}}`.
  - `{{notes}}`.
- Other items, one per line of `audit/<week>/review_items.md`, between `<!-- each review_items -->` and `<!-- end review_items -->`:
  - `{{text}}`.
- Include every row with `unmatched`, `duplicate` or `needs_review` status, plus applicable hours review items; use the Auditor's final review list.
- For an unreadable expense, ask for a clearer source and keep the amount unknown. For a bank only row, do not invent a receipt link.
- Do not suppress a review item because a known amount is already counted in totals.

## Population and verification rules

- Until a real run exists, use the figures in data/answer_key/answer_key.md and label each one as a sample. Never invent a figure. Final run evidence must still be checked against that key.
- The currently merged answer key is an independently verified draft awaiting Sharon's business sign off; it is not an approved release or proof of an end to end run.
- Copy calculated values; do not calculate totals, convert time or project earnings inside these layout notes.
- Apply the documented display conventions through the established calculation and output process: ringgit with two decimal places, hours with one, percentages whole, halves away from zero.
- Empty means unknown or not applicable, not a numeric zero. Keep legitimate calculated zero values distinct from missing evidence.
- Preserve source references, the static caveat and review coverage when the layout becomes the template.
- Demo data only; no private documents, credentials or authoring credits.

## Sources

- Human language design principle: `docs/PLAN.md`, section 2.
- Scope and validation: `docs/PLAN.md`, sections 4 and 10.
- Display conventions, hours and financial bases: `docs/SYSTEM_DESIGN.md`, sections 2, 4.2 and 4.3.
- Agent authority, approval by reply and fixed output order: `docs/SYSTEM_DESIGN.md`, sections 5, 6.1 and 7.
- Raise projections, an agreed design not built: `docs/SYSTEM_DESIGN.md`, section 8.
- Current fixture status and unknown expense limitation: `data/answer_key/answer_key.md`, “Validation and limitations”; fixture evidence does not replace the source of truth docs.
- Visual hierarchy: Damian's provisional approval of the format neutral wireframe.
