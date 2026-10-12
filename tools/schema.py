"""Sheets, columns and fixed value lists from docs/SYSTEM_DESIGN.md, Data Model."""

PLAN_SHEETS = {
    "products": [
        "product_id", "name", "price_rm", "material_cost_rm",
        "packaging_cost_rm", "minutes_per_unit",
    ],
    "channels": [
        "channel", "fee_percent", "fee_per_order_rm",
        "shipping_cost_per_order_rm", "fulfilment_minutes_per_order",
    ],
    "assumptions": [
        "admin_hours_per_week", "planned_margin_percent", "target_hourly_rate_rm",
    ],
    "change_log": [
        "changed_at", "field", "old_value", "new_value", "reason", "source",
    ],
}

LEDGER_SHEETS = {
    "transactions": [
        "txn_id", "date", "type", "category", "description", "product_id",
        "quantity", "amount_rm", "channel", "payment_method", "counterparty",
        "reference", "source_file", "reconciliation_status", "bank_reference",
        "notes",
    ],
    "bank_lines": ["date", "description", "type", "amount_rm", "bank_reference"],
    "hours": [
        "entry_id", "date", "person", "activity", "product_id", "quantity",
        "minutes", "source", "assumption_ref",
    ],
}

# Written as numbers in spreadsheets so the student and judges can sum them.
MONEY_COLUMNS = {
    "price_rm", "material_cost_rm", "packaging_cost_rm", "fee_per_order_rm",
    "shipping_cost_per_order_rm", "target_hourly_rate_rm", "amount_rm",
}
NUMBER_COLUMNS = {
    "minutes_per_unit", "fee_percent", "fulfilment_minutes_per_order",
    "admin_hours_per_week", "planned_margin_percent", "quantity", "minutes",
}

EXPENSE_CATEGORIES = [
    "materials", "packaging", "platform_fees", "shipping", "other_expenses",
]
CATEGORIES = ["sales"] + EXPENSE_CATEGORIES
PAYMENT_METHODS = ["cash", "bank_transfer"]
ACTIVITIES = ["production", "fulfilment", "event", "admin"]
REVIEW_STATUSES = ["unmatched", "duplicate", "needs_review"]
CORRECTABLE_COLUMNS = [
    "minutes_per_unit", "fulfilment_minutes_per_order", "admin_hours_per_week",
]

PERSON = "person_1"
