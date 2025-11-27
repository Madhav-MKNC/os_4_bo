import os
import re
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics

# data loader
from labels import fetch_address

# --- CONSTANTS ---
FROM_ADDRESS = (
    "Satlok Ashram, Satlok Naamdeen Centre, 62, Marasandra Doddaballapur Main Road Bangalore Rural, Karnataka 562163, India, 8884445281"
)

PAGE_W, PAGE_H = 4 * inch, 6 * inch
PAD = 0.20 * inch
BORDER_PT = 2
DIVIDER_PT = 1
LEADING = 1.30

FONT_REG = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

FS_TO = 10
FS_ITEM = 11
FS_FROM = 10
FS_LABEL = 11  # "To:" / "From:" (bold)

# --- Regex helpers (case-insensitive) ---
# --- Parsing helpers (case-insensitive) ---
DIST_RX = re.compile(
    r"\b(?:dist|district)\s*[:\-]?\s*([A-Za-z ]+?)(?=\s*(?:pin(?:\s*code)?|pincode|ph|phone|mob|mobile)\b|[\d,]|$)",
    re.IGNORECASE,
)
PIN_RX  = re.compile(r"\b(?:pin|pin\s*code|pincode)\s*[:\-]?\s*(\d{6})\b", re.IGNORECASE)
PH_RX   = re.compile(r"\b(?:ph|phone|mob|mobile)\s*[:\-]?\s*([+0-9][0-9 \-]{6,})", re.IGNORECASE)


def _clean_spaces(s: str) -> str:
    s = s.replace("\n", " ").replace(",", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def _remove_spans(text: str, spans):
    if not spans:
        return text
    spans = sorted(spans)
    out, prev = [], 0
    for a, b in spans:
        out.append(text[prev:a])
        prev = b
    out.append(text[prev:])
    return "".join(out)

def parse_to_blocks(raw: str):
    """
    Returns (residual_address, structured_lines_text).
    residual = original address with dist/pin/phone fragments removed.
    structured = newline-joined District/Pin/Phone (only if present).
    """
    original = raw
    s = _clean_spaces(original)

    spans = []
    dist = pin = phone = None

    m = DIST_RX.search(s)
    if m:
        dist = m.group(1).strip(" ,.-")
        spans.append(m.span())

    m = PIN_RX.search(s)
    if m:
        pin = m.group(1)
        spans.append(m.span())

    m = PH_RX.search(s)
    if m:
        phone = re.sub(r"[ \-]+", " ", m.group(1)).strip()
        spans.append(m.span())

    residual = _remove_spans(s, spans)
    residual = _clean_spaces(residual) or _clean_spaces(original)

    structured = []
    if dist: structured.append(f"District: {dist}")
    if pin:  structured.append(f"Pin: {pin}")
    if phone: structured.append(f"Phone: {phone}")

    return residual, "\n".join(structured)

# --- layout helpers ---
def wrap(text, font, size, max_width):
    out = []
    paras = text.splitlines() if text else [""]
    for para in paras:
        words = para.split()
        if not words:
            out.append("")
            continue
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if pdfmetrics.stringWidth(test, font, size) <= max_width or not line:
                line = test
            else:
                out.append(line)
                line = w
        if line:
            out.append(line)
    return out

def draw_left(c, x, y, w, text, size):
    lines = wrap(text, FONT_REG, size, w)
    c.setFont(FONT_REG, size)
    for ln in lines:
        c.drawString(x, y - size, ln)
        y -= size * LEADING
    return y

def draw_right(c, x, y, w, text, size):
    lines = wrap(text, FONT_REG, size, w)
    c.setFont(FONT_REG, size)
    for ln in lines:
        tw = pdfmetrics.stringWidth(ln, FONT_REG, size)
        c.drawString(x + w - tw, y - size, ln)
        y -= size * LEADING
    return y

# --- draw one label exactly like the screenshot ---
def draw_label(c, to_raw, from_text, item_text):
    # border
    c.setLineWidth(BORDER_PT)
    c.rect(BORDER_PT/2, BORDER_PT/2, PAGE_W - BORDER_PT, PAGE_H - BORDER_PT)

    x = PAD
    w = PAGE_W - 2 * PAD

    # ============================================================
    # 1) MEASURE TOP BLOCK (TO header + TO text)
    # ============================================================
    # header height
    to_header_h = FS_LABEL * LEADING

    # text lines
    residual, structured = parse_to_blocks(to_raw)
    to_lines_1 = wrap(residual, FONT_REG, FS_TO, w)
    to_lines_2 = wrap(structured, FONT_REG, FS_TO, w) if structured else []

    to_text_h = (len(to_lines_1) + len(to_lines_2)) * (FS_TO * LEADING)

    top_block_h = to_header_h + to_text_h


    # ============================================================
    # 2) MEASURE BOTTOM BLOCK (FROM header + FROM text)
    # ============================================================
    from_header_h = FS_LABEL * LEADING
    from_lines = wrap(from_text, FONT_REG, FS_FROM, w)
    from_text_h = len(from_lines) * (FS_FROM * LEADING)
    bottom_block_h = from_header_h + from_text_h


    # ============================================================
    # 3) DETERMINE AVAILABLE MIDDLE HEIGHT
    #    (for item + divider + spacing around them)
    # ============================================================
    used_top = top_block_h
    used_bottom = bottom_block_h
    free_middle = PAGE_H - 2*PAD - used_top - used_bottom

    # middle padding top/bottom
    mid_pad = free_middle * 0.3
    # item block
    item_h = FS_ITEM * LEADING
    # divider line spacing
    divider_pad = free_middle * 0.10

    # Y start for drawing
    y = PAGE_H - PAD

    # ============================================================
    # DRAW — TOP BLOCK
    # ============================================================
    # "To:"
    c.setFont(FONT_BOLD, FS_LABEL)
    c.drawString(x, y - FS_LABEL, "To:")
    y -= to_header_h

    # TO text
    y = draw_left(c, x, y, w, residual, FS_TO)
    if structured:
        y = draw_left(c, x, y, w, structured, FS_TO)

    # Middle padding before item
    y -= mid_pad


    # ============================================================
    # DRAW — ITEM
    # ============================================================
    y = draw_left(c, x, y, w, item_text, FS_ITEM)

    # spacing to divider
    y -= divider_pad

    # divider line
    c.setLineWidth(DIVIDER_PT)
    c.line(x, y, x + w, y)
    y -= divider_pad


    # ============================================================
    # DRAW — BOTTOM BLOCK (FROM aligned to bottom)
    # ============================================================
    # bottom anchor
    # yf = PAD + bottom_block_h
    yf = PAD + bottom_block_h + 0.75*inch

    # "From:"
    c.setFont(FONT_BOLD, FS_LABEL)
    lab_w = pdfmetrics.stringWidth("From:", FONT_BOLD, FS_LABEL)
    c.drawString(x + w - lab_w, yf - FS_LABEL, "From:")
    yf -= from_header_h

    # FROM text
    draw_right(c, x, yf, w, from_text, FS_FROM)

# --- public API ---
def generate_label_pdf(input_path, output_folder):
    """
    Reads data from input_path (CSV), generates a PDF in output_folder.
    Returns the filename of the generated PDF.
    """
    data = fetch_address.get_data(input_path)

    base = os.path.splitext(os.path.basename(input_path))[0]
    out_name = f"LABELS_{base}.pdf"
    out_path = os.path.join(output_folder, out_name)

    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    for row in data:
        to_text = str(row.get("to", "")).strip()
        item_text = str(row.get("item", "")).strip()
        from_text = FROM_ADDRESS.strip()
        draw_label(c, to_text, from_text, item_text)
        c.showPage()
    c.save()
    return out_name

# optional CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python make_labels.py <input.csv> <output_folder>")
        sys.exit(1)
    infile, outdir = sys.argv[1], sys.argv[2]
    print(os.path.join(outdir, generate_label_pdf(infile, outdir)))
