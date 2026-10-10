"""Render expense receipt PNGs with Pillow 12.3.0 and its bundled default font.

Run this file with Python from any directory. No external assets, random input,
clock values, PNG metadata, or intermediate images are used.
"""

import hashlib
import io
import json
from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


HERE = Path(__file__).resolve().parent
OUTPUT = HERE.parents[2] / "data" / "demo" / "inbox"
LABEL = "SYNTHETIC DEMO - NOT A REAL RECEIPT"
SIZE = (1000, 1120)
PAPER = (250, 248, 243)
INK = (35, 36, 34)
MUTED = (100, 99, 94)
BAND_BOX = (60, 746, 940, 922)
DUPLICATES = {"T0004": "T0003"}
BLURRED = "T0012"
FONTS = {size: ImageFont.load_default(size=size) for size in (23, 28, 32, 44)}


def draw_point(draw, text, y):
    """Wrap a single point with a hanging indent, without a table layout."""
    font = FONTS[32]
    line = "-"
    for word in text.split():
        candidate = line + " " + word
        if draw.textlength(candidate, font=font) > 852:
            draw.text((74, y), line, font=font, fill=INK)
            y += 44
            line = "  " + word
        else:
            line = candidate
    draw.text((74, y), line, font=font, fill=INK)
    return y + 76


def total_band(amount, blurred):
    width = BAND_BOX[2] - BAND_BOX[0]
    height = BAND_BOX[3] - BAND_BOX[1]
    band = Image.new("RGB", (width, height), (236, 233, 226))
    draw = ImageDraw.Draw(band)
    if blurred:
        if amount is not None:
            raise ValueError("The blurred source amount must remain unknown")
        # Disposable typography only, not an estimate or a source amount.
        # The clear raster exists only in memory and is never encoded or saved.
        text = "- Amount: RM 00.00"
    else:
        if amount is None:
            raise ValueError("A readable receipt requires an explicit source amount")
        text = f"- Amount: RM {Decimal(str(amount)):.2f}"
    draw.text((24, 59), text, font=FONTS[44], fill=INK)
    del draw

    if blurred:
        # Collapse the ENTIRE band to one pixel, then quantize away fine values.
        # No horizontal or vertical digit structure survives this operation.
        collapsed = band.resize((1, 1), Image.Resampling.BOX)
        collapsed = ImageOps.posterize(collapsed, bits=2)
        band.close()
        band = collapsed.resize((width, height), Image.Resampling.NEAREST)
        band = band.filter(ImageFilter.GaussianBlur(radius=28))
        assert all(low == high for low, high in band.getextrema())

        # Feather only the edges of the already destroyed band into the paper.
        mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (18, 18, width - 19, height - 19), radius=26, fill=255
        )
        mask = mask.filter(ImageFilter.GaussianBlur(radius=18))
        band = Image.composite(band, Image.new("RGB", band.size, PAPER), mask)
    return band


def render(row):
    blurred = row["txn_id"] == BLURRED
    image = Image.new("RGB", SIZE, PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((28, 28, 971, 1091), outline=(205, 202, 195), width=2)
    draw.rectangle((48, 48, 951, 124), fill=INK)
    draw.text((500, 84), LABEL, font=FONTS[28], fill=PAPER, anchor="mm")
    draw.text((72, 171), "PURCHASE RECEIPT", font=FONTS[44], fill=INK)
    draw.line((72, 246, 928, 246), fill=(188, 185, 179), width=2)

    description = row["description"]
    if blurred:
        # This suffix is an intake annotation, not purchase information.
        description = description.removesuffix("; total unreadable")
    points = [
        f"Date: {row['date']}",
        f"Supplier: {row['counterparty']}",
        f"Purchase: {description}",
        f"Payment: {row['payment_method'].replace('_', ' ').capitalize()}",
    ]
    if row.get("reference"):
        points.append(f"Reference: {row['reference']}")
    y = 294
    for point in points:
        y = draw_point(draw, point, y)
    if y > BAND_BOX[1]:
        raise ValueError("Receipt details overlap the total band")

    image.paste(total_band(row["amount_rm"], blurred), BAND_BOX[:2])
    draw.line((72, 958, 928, 958), fill=(188, 185, 179), width=2)
    draw.text((72, 985), "All names are invented.", font=FONTS[23], fill=MUTED)
    draw.text((72, 1032), LABEL, font=FONTS[23], fill=INK)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()


def build_receipts(manifest):
    rows = [
        row
        for row in manifest["raw_documents"]
        if row["type"] == "expense" and (row.get("source_file") or "").endswith(".png")
    ]
    by_id = {row["txn_id"]: row for row in rows}
    basenames = [Path(row["source_file"]).name for row in rows]
    if len(set(basenames)) != len(basenames):
        raise ValueError("Receipt basenames must be unique")

    encoded = {}
    comparable = (
        "date", "counterparty", "description", "payment_method", "reference", "amount_rm"
    )
    for row in rows:
        txn_id = row["txn_id"]
        if txn_id in DUPLICATES:
            original = by_id[DUPLICATES[txn_id]]
            if any(row[field] != original[field] for field in comparable):
                raise ValueError("Duplicate receipt fields differ from the original")
            continue
        encoded[txn_id] = render(row)

    for duplicate, original in DUPLICATES.items():
        if duplicate in by_id:
            encoded[duplicate] = encoded[original]
    return {Path(row["source_file"]).name: encoded[row["txn_id"]] for row in rows}


def main():
    if not OUTPUT.is_dir():
        raise FileNotFoundError(f"Receipt output directory must exist: {OUTPUT}")
    manifest = json.loads((HERE / "render_manifest.json").read_text(encoding="utf-8"))
    outputs = build_receipts(manifest)
    if outputs != build_receipts(manifest):
        raise RuntimeError("Receipt rendering is not deterministic")

    # Refuse to overwrite unrelated existing content; identical reruns are safe.
    for name, payload in outputs.items():
        target = OUTPUT / name
        if target.exists() and target.read_bytes() != payload:
            raise FileExistsError(f"Existing receipt differs; not overwriting: {target}")
        with Image.open(io.BytesIO(payload)) as image:
            image.load()
            if image.info or image.size != SIZE or image.mode != "RGB":
                raise RuntimeError(f"Unexpected PNG properties: {name}")

    for name, payload in outputs.items():
        target = OUTPUT / name
        if not target.exists():
            target.write_bytes(payload)
        if target.read_bytes() != payload:
            raise RuntimeError(f"Saved receipt bytes differ: {name}")
        print(f"- {name}: SHA-256 {hashlib.sha256(payload).hexdigest()}")
    print("Checks passed: deterministic bytes; RGB PNGs; no PNG metadata.")
    print("Duplicate uses original PNG bytes; unknown source amount remains unset.")


if __name__ == "__main__":
    main()
