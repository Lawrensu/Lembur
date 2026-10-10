# Answer key - 2026-W41

- Status: independently verified draft; awaiting Sharon's business sign-off. Do not treat as an approved release yet.
- Synthetic demonstration only. Aisyah and all customers and suppliers are fictional. Channel costs are approved scenario assumptions, not statements of platform pricing.
- Dates: Monday 2026-10-05 through Sunday 2026-10-11, Malaysia time.
- Sources of truth: docs/PLAN.md section 10; docs/SYSTEM_DESIGN.md sections 2 to 4.
- Fixture: 20 transactions, 14 bank lines, 20 hours lines; 14 separate single-product sales orders.
- Money uses integer sen; time uses integer minutes; display uses half-away-from-zero rounding. Never divide by rounded displayed hours.

## Validation and limitations

- Primary and independent calculations: 106 exact comparisons passed; zero differences, including all hours fields, money, statuses and bank references.
- Independent calculator received only the two source-of-truth docs, baseline plan, messages, and isolated transactions/bank_lines sheets. It did not receive expected hours, the first calculator, or this answer key.
- Rule checker covers every planted problem and every dataset rule. See .expected_ledger.ref/rule_check.md for results and visual-inspection limitations.
- This validates the fixture, not Law's extraction workflow, model OCR accuracy, trigger reliability, or an observed end-to-end run. Those remain to be tested against this key.
- The blurry expense has an unknown amount, not a zero expense. Take home and hourly rate are provisional known-amount results; true earnings may be lower once the receipt is readable.
- No projected raise or Day Zero formula is used. Both designs are agreed in design section 8 but not built.

## Ledger totals by category

- sales: RM108.50; counted rows: T0001, T0002, T0005, T0006, T0007, T0008, T0010, T0011, T0013, T0015, T0016, T0017, T0018, T0019.
- materials: RM27.00; counted rows: T0003, T0020.
- packaging: RM6.00; counted rows: T0009.
- platform_fees: RM0.00; counted rows: none.
- shipping: RM36.00; counted rows: T0014.
- other_expenses: RM0.00; counted rows: none.
- Total counted expenses: RM69.00.
- Take home: RM108.50 minus RM69.00 = RM39.50.
- Hourly rate: RM39.50 / 938 minutes * 60 = RM2.53/hour.
- Margin: take home / sales * 100 = 36% displayed; plan 40%.
- Hourly-rate comparison: RM2.53 actual against RM12.00 target.

## Planted problems and final review list

- T0004, duplicate receipt: duplicate of T0003; both document amounts RM18.00, same date, counterparty and reference DEMO-OUT-001. Keep both images filed; exclude T0004 from totals and hours. Review: confirm the second upload is a copy.
- T0012, blurry receipt: needs_review; amount_rm stays empty. Intake flag takes precedence over cash_declared. Exclude from totals; retain receipts/2026-10/receipt_thread_blurred.png. Review: request a legible original, do not estimate the amount.
- T0019, amount mismatch: needs_review; document RM5.00 and bank RM4.50 share DEMO-IN-010. Keep both amounts in notes, use RM4.50 in totals, and count the single sold keychain for hours. Review: confirm whether the difference is an underpayment or another error.
- T0020, missing receipt: unmatched; bank DEMO-OUT-004 identifies Demo Bead Nook and bead materials. Sunday leftover-bank row is a materials expense of RM9.00, included in totals, with source_file empty. Review: request the missing receipt.
- Final review IDs, exactly: T0004, T0012, T0019, T0020.
- Bestseller that loses money: P01; see product results below. It is a product warning, not a new reconciliation status.
- Event: H0017; Saturday 10am to 6pm gives 480 stated minutes; message.2026-10-10.
- Correction: Wednesday's one reply changes products.P01.minutes_per_unit from 20 to 15. Sales exist before and after the effective date.

## Correction and plan state

- The input, the plan CSV files data/demo/plan_*.csv, is the baseline: P01=20 and change_log has headers only.
- The run's workspace/plan/plan_*.csv ends with P01=15 and exactly one change_log row: changed_at=2026-10-07; field=products.P01.minutes_per_unit; old_value=20; new_value=15; reason=I timed myself today, keychains take 15 minutes not 20; source=message.2026-10-07.
- Sharon-approved clarification of design wording: pre-correction P01 lines use 20 and source=estimate; on/after October 7 use 15 and source=corrected. Historical baseline values are not retroactively labelled corrected. Design section 4.2 states this rule.
- Other production, fulfilment and admin lines remain estimate. Only the bazaar event is stated. No extra stated production hours are added.

## Every expected hours line

- H0001: 2026-10-05; production; product=P01; quantity=2; 40 minutes; source=estimate; assumption_ref=products.P01.minutes_per_unit.
- H0002: 2026-10-05; fulfilment; product=P01; quantity=2; 10 minutes; source=estimate; assumption_ref=channels.instagram.fulfilment_minutes_per_order.
- H0003: 2026-10-06; production; product=P01; quantity=2; 40 minutes; source=estimate; assumption_ref=products.P01.minutes_per_unit.
- H0004: 2026-10-06; production; product=P02; quantity=1; 35 minutes; source=estimate; assumption_ref=products.P02.minutes_per_unit.
- H0005: 2026-10-06; fulfilment; product=P01; quantity=2; 10 minutes; source=estimate; assumption_ref=channels.instagram.fulfilment_minutes_per_order.
- H0006: 2026-10-06; fulfilment; product=P02; quantity=1; 5 minutes; source=estimate; assumption_ref=channels.instagram.fulfilment_minutes_per_order.
- H0007: 2026-10-07; production; product=P01; quantity=1; 15 minutes; source=corrected; assumption_ref=products.P01.minutes_per_unit.
- H0008: 2026-10-07; fulfilment; product=P01; quantity=1; 5 minutes; source=estimate; assumption_ref=channels.instagram.fulfilment_minutes_per_order.
- H0009: 2026-10-08; production; product=P01; quantity=1; 15 minutes; source=corrected; assumption_ref=products.P01.minutes_per_unit.
- H0010: 2026-10-08; production; product=P02; quantity=1; 35 minutes; source=estimate; assumption_ref=products.P02.minutes_per_unit.
- H0011: 2026-10-08; fulfilment; product=P01; quantity=1; 5 minutes; source=estimate; assumption_ref=channels.instagram.fulfilment_minutes_per_order.
- H0012: 2026-10-08; fulfilment; product=P02; quantity=1; 3 minutes; source=estimate; assumption_ref=channels.telegram.fulfilment_minutes_per_order.
- H0013: 2026-10-09; production; product=P01; quantity=1; 15 minutes; source=corrected; assumption_ref=products.P01.minutes_per_unit.
- H0014: 2026-10-09; fulfilment; product=P01; quantity=1; 5 minutes; source=estimate; assumption_ref=channels.instagram.fulfilment_minutes_per_order.
- H0015: 2026-10-10; production; product=P01; quantity=3; 45 minutes; source=corrected; assumption_ref=products.P01.minutes_per_unit.
- H0016: 2026-10-10; production; product=P02; quantity=1; 35 minutes; source=estimate; assumption_ref=products.P02.minutes_per_unit.
- H0017: 2026-10-10; event; product=empty; quantity=empty; 480 minutes; source=stated; assumption_ref=message.2026-10-10.
- H0018: 2026-10-11; production; product=P01; quantity=1; 15 minutes; source=corrected; assumption_ref=products.P01.minutes_per_unit.
- H0019: 2026-10-11; fulfilment; product=P01; quantity=1; 5 minutes; source=estimate; assumption_ref=channels.instagram.fulfilment_minutes_per_order.
- H0020: 2026-10-11; admin; product=empty; quantity=empty; 120 minutes; source=estimate; assumption_ref=assumptions.admin_hours_per_week.
- production total: 290 minutes.
- fulfilment total: 48 minutes.
- event total: 480 minutes.
- admin total: 120 minutes.
- Week total: 938 minutes; 15.6 hours displayed.
- Shared event plus admin: 600 minutes; not allocated to products.

## Product profit and direct hourly earnings

- P01 - Beaded keychain:
  - Units sold: 11; revenue RM54.50.
  - Unit costs: RM33.00; channel costs: RM32.00.
  - Profit: RM-10.50; loses money: yes.
  - Direct time: 185 production + 40 fulfilment = 225 minutes.
  - Profit / direct minutes * 60: RM-2.80/hour.
- P02 - Beaded bracelet:
  - Units sold: 3; revenue RM54.00.
  - Unit costs: RM18.00; channel costs: RM4.00.
  - Profit: RM32.00; loses money: no.
  - Direct time: 105 production + 8 fulfilment = 113 minutes.
  - Profit / direct minutes * 60: RM16.99/hour.
- Two bases, on purpose: take home uses actual ledger purchases; product profit uses plan per-unit costs and per-order channel costs. Product profits do not add up to take home; shared time is excluded from product hourly rates.

## Expected Auditor direction

- Uphold Payroll against expanding the existing keychain mix merely because P01 sold 11 units. P01 loses RM10.50; its direct hourly profit is RM-2.80.
- Support prioritising bracelet promotion: P02 earns RM32.00 and RM16.99 per direct hour. Do not present this as the whole-business hourly rate.
- Support moving low-priced keychains to campus pickup/bazaar or reviewing delivered pricing before more promotion. Draft changes for approval; do not send or post.
- Reject unsupported claims about future demand or a precise hourly raise. A positive product profit alone does not justify expanding an eight-hour event.
- Preserve all four review entries and the unknown-expense caveat in the payslip.

## Bank matching and every transaction status

- Transaction IDs follow intake order: inbox files in file name order, then rows that come only from the message.
- Dana and Mira have same-amount nearby bank candidates and no printed references. Resolve by the fictional customer name in the bank description. Both are ambiguous_resolved; reference-bearing transfers match directly.
- T0001: 2026-10-05; ambiguous_resolved; RM5.00; bank_reference=DEMO-IN-001; source_file=receipts/2026-10/order_2026-10-05_dana.png.
- T0002: 2026-10-05; ambiguous_resolved; RM5.00; bank_reference=DEMO-IN-002; source_file=receipts/2026-10/order_2026-10-05_mira.png.
- T0003: 2026-10-05; matched; RM18.00; bank_reference=DEMO-OUT-001; source_file=receipts/2026-10/receipt_beads.png.
- T0004: 2026-10-05; duplicate; RM18.00; bank_reference=empty; source_file=receipts/2026-10/receipt_beads_copy.png.
- T0005: 2026-10-06; matched; RM5.00; bank_reference=DEMO-IN-003; source_file=receipts/2026-10/order_2026-10-06_farah.png.
- T0006: 2026-10-06; matched; RM18.00; bank_reference=DEMO-IN-005; source_file=receipts/2026-10/order_2026-10-06_hana.png.
- T0007: 2026-10-06; matched; RM5.00; bank_reference=DEMO-IN-004; source_file=receipts/2026-10/order_2026-10-06_nisa.png.
- T0008: 2026-10-07; matched; RM5.00; bank_reference=DEMO-IN-006; source_file=receipts/2026-10/order_2026-10-07_iman.png.
- T0009: 2026-10-07; matched; RM6.00; bank_reference=DEMO-OUT-002; source_file=receipts/2026-10/receipt_pouches.png.
- T0010: 2026-10-08; matched; RM5.00; bank_reference=DEMO-IN-007; source_file=receipts/2026-10/order_2026-10-08_lina.png.
- T0011: 2026-10-08; matched; RM18.00; bank_reference=DEMO-IN-008; source_file=receipts/2026-10/order_2026-10-08_rina.png.
- T0012: 2026-10-08; needs_review; empty (unknown); bank_reference=empty; source_file=receipts/2026-10/receipt_thread_blurred.png.
- T0013: 2026-10-09; matched; RM5.00; bank_reference=DEMO-IN-009; source_file=receipts/2026-10/order_2026-10-09_suri.png.
- T0014: 2026-10-09; matched; RM36.00; bank_reference=DEMO-OUT-003; source_file=receipts/2026-10/receipt_shipping.png.
- T0015: 2026-10-10; cash_declared; RM5.00; bank_reference=empty; source_file=receipts/2026-10/message_2026-10-10.txt.
- T0016: 2026-10-10; cash_declared; RM5.00; bank_reference=empty; source_file=receipts/2026-10/message_2026-10-10.txt.
- T0017: 2026-10-10; cash_declared; RM5.00; bank_reference=empty; source_file=receipts/2026-10/message_2026-10-10.txt.
- T0018: 2026-10-10; cash_declared; RM18.00; bank_reference=empty; source_file=receipts/2026-10/message_2026-10-10.txt.
- T0019: 2026-10-11; needs_review; RM4.50; bank_reference=DEMO-IN-010; source_file=receipts/2026-10/order_2026-10-11_zahra.png.
- T0020: 2026-10-11; unmatched; RM9.00; bank_reference=DEMO-OUT-004; source_file=empty.

## Reproduction and handoff

- The CSV files data/demo/plan_*.csv and data/answer_key/ledger_*.csv are the source of truth, and data/test_harness/compare_outputs.py checks a run against them with no installed package. The scripts listed below built the first .xlsx version and still need openpyxl and Pillow.
- Run the scripts using a Python environment with openpyxl and Pillow installed; paths below are relative to the repository root. No runtime app or skills are installed by this fixture.
- Baseline workbook: data/demo/.plan.ref/build.py.
- Expected ledger and primary numbers: data/answer_key/.expected_ledger.ref/build.py.
- Derived sources: render_receipts.py, render_orders.py and render_bank.py in data/answer_key/.expected_ledger.ref/.
- Nightly text and intake batches: data/demo/messages.md.
- Independent rebuild: data/answer_key/.independent.ref/independent_calc.py, using its isolated two-sheet input. Refresh that isolated input from transactions and bank_lines if the fixture changes; never include expected hours or primary calculation code.
- Rule checks: data/answer_key/.expected_ledger.ref/check_rules.py.
- Exact comparison and this draft: data/answer_key/.expected_ledger.ref/verify_and_write_key.py.
- Run inputs only: copy baseline plan and each day's inbox batch/message into workspace. Never copy data/answer_key into workspace or give it to the production agents during the demo.
- Next gate: Sharon signs off on the story and answer key. Later, compare Law's real outputs row-by-row, including amounts to the sen, statuses, sources and minutes. No observed-run comparison has happened yet.
