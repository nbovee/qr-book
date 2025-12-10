#!/usr/bin/env -S uv run python
"""
QR Code PDF Generator

Generates PDF pages with QR codes containing UUID v4 values,
with blank info boxes for handwriting notes.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = "output"

try:
    import qrcode
    from uuid import uuid4
    from PIL import Image
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Please install dependencies: pip install qrcode[pil] reportlab")
    sys.exit(1)


LAYOUT = {
    "page_width": 612,
    "page_height": 792,
    "margin_top": 36,
    "margin_bottom": 36,
    "margin_left": 72,
    "margin_right": 36,
    "qr_size": 60,
    "box_width": 504,
    "box_height": 72,
    "qr_padding": 6,
    "row_spacing": 72,
    "codes_per_page": 10,
}


def generate_uuid4_without_dashes() -> str:
    """Generate UUID v4 as 32-character hex string without dashes."""
    return uuid4().hex


def create_qr_code(data: str, size: int = 60) -> Image.Image:
    """Generate high-resolution QR code image."""
    high_res_size = size * 4

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image = qr_image.convert("RGB")
    qr_image = qr_image.resize((high_res_size, high_res_size), Image.LANCZOS)
    return qr_image


def get_timestamped_filename(base_filename: str) -> str:
    """Generate timestamped filename (e.g., qr-codes-20250109-143022.pdf)."""
    path = Path(base_filename)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{path.stem}-{timestamp}{path.suffix}"


def generate_pdf(
    num_pages: int,
    output_filename: str,
    start_page: int = 1,
    double_sided: bool = False,
) -> None:
    """Generate PDF with QR codes and optional double-sided margin flipping."""
    c = canvas.Canvas(output_filename, pagesize=letter)
    width, height = LAYOUT["page_width"], LAYOUT["page_height"]

    total_codes = num_pages * LAYOUT["codes_per_page"]

    print(f"Generating {num_pages} page(s) with {total_codes} QR codes...")
    print(f"Page numbering starts at: {start_page}")
    if double_sided:
        print("Double-sided mode: margins will flip on even pages")

    for page_num in range(num_pages):
        if num_pages > 1:
            print(f"  Page {page_num + 1}/{num_pages}...")

        actual_page_num = start_page + page_num

        if double_sided and actual_page_num % 2 == 0:
            margin_left = LAYOUT["margin_right"]
            margin_right = LAYOUT["margin_left"]
        else:
            margin_left = LAYOUT["margin_left"]
            margin_right = LAYOUT["margin_right"]

        box_width = width - margin_left - margin_right

        for row in range(LAYOUT["codes_per_page"]):
            uuid_str = generate_uuid4_without_dashes()
            qr_img = create_qr_code(uuid_str, size=LAYOUT["qr_size"])

            y_box = (
                height
                - LAYOUT["margin_top"]
                - (row * LAYOUT["row_spacing"])
                - LAYOUT["box_height"]
            )
            x_box = margin_left

            c.rect(x_box, y_box, box_width, LAYOUT["box_height"], stroke=1, fill=0)

            if row % 2 == 0:
                x_qr = x_box + LAYOUT["qr_padding"]
            else:
                x_qr = x_box + box_width - LAYOUT["qr_size"] - LAYOUT["qr_padding"]

            y_qr = y_box + LAYOUT["qr_padding"]

            c.drawInlineImage(
                qr_img,
                x_qr,
                y_qr,
                width=LAYOUT["qr_size"],
                height=LAYOUT["qr_size"],
                preserveAspectRatio=True,
            )

        c.setFont("Helvetica", 10)
        page_text = f"Page {actual_page_num}"
        text_width = c.stringWidth(page_text, "Helvetica", 10)
        c.drawString(
            width - margin_right - text_width, LAYOUT["margin_bottom"] - 20, page_text
        )

        c.showPage()

    c.save()
    print(f"Successfully generated {output_filename}")
    print(f"Total: {num_pages} page(s), {total_codes} QR codes")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate PDF with QR codes for item tracking",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-n", "--num-pages", type=int, default=1, help="Number of pages to generate"
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="qr-codes.pdf",
        help="Base output PDF filename (will be timestamped)",
    )

    parser.add_argument(
        "-s",
        "--start-page",
        type=int,
        default=1,
        help="Starting page number for numbering",
    )

    parser.add_argument(
        "-d",
        "--double-sided",
        action="store_true",
        help="Enable double-sided printing (flips margins on even pages)",
    )

    args = parser.parse_args()

    if args.num_pages < 1:
        parser.error("Number of pages must be at least 1")
    if args.num_pages > 100:
        print(f"Warning: Generating {args.num_pages} pages. This may take a while...")
    if args.start_page < 1:
        parser.error("Starting page number must be at least 1")

    return args


def main() -> None:
    args = parse_arguments()

    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    timestamped_name = get_timestamped_filename(args.output)
    output_filename = str(output_dir / timestamped_name)

    try:
        generate_pdf(
            args.num_pages, output_filename, args.start_page, args.double_sided
        )
    except Exception as e:
        print(f"Error generating PDF: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
