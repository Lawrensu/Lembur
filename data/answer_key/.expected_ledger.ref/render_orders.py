import json
from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = Path(__file__).with_name("render_manifest.json")
OUTPUT = ROOT / "data" / "demo" / "inbox"
WARNING = "SYNTHETIC DEMO - NOT A REAL ORDER"
WIDTH = 1080
REGULAR = "C:/Windows/Fonts/segoeui.ttf"
BOLD = "C:/Windows/Fonts/segoeuib.ttf"
BODY_FONT = ImageFont.truetype(REGULAR, 30)
LABEL_FONT = ImageFont.truetype(BOLD, 30)
TITLE_FONT = ImageFont.truetype(BOLD, 46)
WARNING_FONT = ImageFont.truetype(BOLD, 30)


def order_fields(row):
    fields = []

    def add(label, key, formatter=str):
        value = row.get(key)
        if value is not None and value != "":
            fields.append((label, formatter(value)))

    add("Date", "date")
    add("Fictional customer", "counterparty")
    add("Channel", "channel", lambda value: value.replace("_", " ").title())
    product = row.get("description")
    if product:
        prefix = f"{row['quantity']} " if row.get("quantity") is not None else ""
        fields.append(("Product", product.removeprefix(prefix)))
    add("Product ID", "product_id")
    add("Quantity", "quantity")
    add("Order amount", "amount_rm", lambda value: f"RM{Decimal(str(value)):.2f}")
    add("Payment method", "payment_method", lambda value: value.replace("_", " ").capitalize())
    add("Payment reference", "reference")
    return fields


def render_order(row):
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    entries = []
    y = 294
    for label, value in order_fields(row):
        label_text = f"{label}: "
        value_x = 112 + measure.textlength(label_text, font=LABEL_FONT)
        available = 956 - value_x
        lines = []
        line = ""
        for word in value.split():
            candidate = f"{line} {word}" if line else word
            if line and measure.textlength(candidate, font=BODY_FONT) > available:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
        entries.append((label_text, lines, value_x, y))
        y += max(88, 44 * len(lines) + 28)

    card_bottom = y + 10
    image = Image.new("RGB", (WIDTH, card_bottom + 52), "#EDF3F1")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((40, 36, 1040, 140), radius=18, fill="#FFF0DA", outline="#B47C27", width=2)
    draw.text((540, 88), WARNING, font=WARNING_FONT, fill="#70400A", anchor="mm")
    draw.text((60, 177), "Order details", font=TITLE_FONT, fill="#193D35")
    draw.rounded_rectangle((48, 250, 1032, card_bottom), radius=24, fill="#FFFFFF", outline="#D5E0DC", width=2)

    for label, lines, value_x, top in entries:
        draw.ellipse((80, top + 17, 88, top + 25), fill="#2C6E5C")
        draw.text((112, top), label, font=LABEL_FONT, fill="#25483F")
        for index, line in enumerate(lines):
            draw.text((value_x, top + index * 44), line, font=BODY_FONT, fill="#253C36")

    return image


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = [
        row for row in manifest["raw_documents"]
        if row.get("category") == "sales"
        and Path(row.get("source_file") or "").suffix.lower() == ".png"
    ]
    names = [Path(row["source_file"]).name for row in rows]
    if len(names) != len(set(names)):
        raise ValueError("Order output basenames must be unique")
    if not OUTPUT.is_dir():
        raise FileNotFoundError(OUTPUT)

    for row, name in zip(rows, names):
        path = OUTPUT / name
        render_order(row).save(path, format="PNG", optimize=False, compress_level=9)
        print(path)
    print(f"Rendered {len(rows)} order PNGs.")


if __name__ == "__main__":
    main()
