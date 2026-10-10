# Payslip handoff to Law and the builder agent

## Status

* From Damian, Role C, to Law, Role A, and the agent handling Payroll integration.
* The handoff template is `submission/payslip_template.html`. It is available in `dev` through PR 11.
* Damian reviewed the sample PDF at 17:23 on 10 October and confirmed “the sample pdf looks good”.
* This approves the sample appearance. It does not establish an observed agent run, verified real figures or correct pagination for every future output.
* Law's receipt, renderer integration and repeatable Payroll PDF conversion remain unconfirmed. Please confirm them explicitly.

## Read before integrating

* Read `README.md`, `docs/PLAN.md` and `docs/SYSTEM_DESIGN.md` in that order. These remain the sources of truth.
* Use SYSTEM_DESIGN section 7 for the field and repeating block contract, and section 6.1 for execution order and approval behaviour.
* Read `submission/payslip_layout.md`, especially “Template integration notes”, for missing values, draft path resolution and screen versus print styling.
* Use the HTML template as the renderer input. The single brace narrative slots in the layout note are not additional template fields.

## Requested action

* Confirm that you have read the template and its integration notes and can accept the handoff.
* Integrate the template through the payslip command referenced by the Payroll skill. If a requirement is missing or contradictory, ask Law rather than adding a field or feature.
* Build the payslip once after the actual Auditor ruling, following SYSTEM_DESIGN section 6.1. Do not create a draft payslip or type figures into it with a model.
* Confirm a repeatable, installation free HTML to PDF method that Payroll can use. If a dependency is required, stop and ask Law first. HTML remains the documented fallback.
* Verify the populated real output with Sharon's approved answer key, and return the populated PDF to Damian for visual review.

## Preserve during integration

* Keep the ten sections in SYSTEM_DESIGN section 7 order and preserve the approved hourly rate first hierarchy.
* Copy numerical scalars from `workspace/audit/<week>/numbers.json`. Use actual recommendation and ruling files, not the answer key's expected dialogue or ruling direction.
* Expand `products`, `review_rows`, `review_items` and `raise_plan` using only the documented fields.
* Include every transaction review row and every line of `workspace/audit/<week>/review_items.md`. Do not hide a review item because its known amount already counts in totals.
* HTML escape substituted text and attribute values. Write missing scalars as genuinely empty strings and loss booleans as lowercase `true` or `false`.
* Supply `draft_file` as a workspace relative path such as `approvals/<week>/01_instagram_post.md`. The template prepends `../` from `workspace/payslips/`; a basename alone or a `workspace/` prefix resolves incorrectly.
* Keep the unknown expense caveat, the explicit loss label, shared hours already included, and the distinction between product profit and ledger based take home.
* Keep individual approval by reply, “approve N” or “skip N”. The system never posts or sends drafts; the student sends an approved draft herself.
* Preserve offline inline styling with no scripts or external assets. The dark screen palette intentionally becomes a light A4 print page.

## PDF preparation evidence

* PLAN section 12, check 11 records sample export and Damian's visual approval.
* WorkBuddy used managed Node 22.22.2 with installed Chrome 154. The browser's `Page.printToPDF` operation used `printBackground: true`, `preferCSSPageSize: true` and `displayHeaderFooter: false`.
* The recorded sample export produced a four page A4 PDF without installations; the last measured export operation took 0.562 seconds. This is sample export timing, not total workflow runtime.
* The sample files are local review evidence, not production inputs or a replacement for the template. Do not copy the answer key into the production agents' workspace.

## Reply requested from Law or the builder agent

* Handoff received and accepted, or the specific blocker.
* Renderer integration status and the resulting HTML path.
* Repeatable PDF conversion method, or the HTML fallback taken.
* Populated output paths and verification status, including ruling text, draft links, review coverage and pagination.
* Any remaining issue requiring Damian's decision. Do not mark acceptance or production validation complete without evidence.
