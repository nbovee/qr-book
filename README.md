# QR Code PDF Generator

Generate PDF pages with QR codes for item tracking. Each page contains 10 QR codes with boxes for handwritten notes.

## Usage

```bash
uv run python main.py [options]
```

## Options

- `-n, --num-pages` - Number of pages to generate (default: 1)
- `-o, --output` - Base filename for PDF (default: qr-codes.pdf)
- `-s, --start-page` - Starting page number (default: 1)
- `-d, --double-sided` - Enable double-sided printing with alternating margins

## Examples

```bash
# Generate 1 page
uv run python main.py

# Generate 5 pages
uv run python main.py -n 5

# Generate pages 10-14 for double-sided printing
uv run python main.py -n 5 -s 10 -d

# Custom filename
uv run python main.py -n 3 -o inventory.pdf
```

## Output

PDFs are saved to the `output/` folder with timestamps:
- `output/qr-codes-20251209-143022.pdf`
- `output/inventory-20251209-143523.pdf`

Each QR code contains a unique UUID (32-character hex string).
