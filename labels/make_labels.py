import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics

# Import the data fetcher
from labels import fetch_address


# TO Address
FROM_ADDRESS = "Satlok Ashram, Satlok Naamdeen Centre, 62, Marasandra, Doddaballapur Main Road, Bangalore Rural, Karnataka 562163, India"

# ---- PAGE + STYLE ----
PAGE_W, PAGE_H = 3*inch, 5*inch         # 3x5 inches
BORDER_PT = 2                            # outer border
DIVIDER_PT = 2                           # lines between sections
PAD = 0.20*inch                          # inner padding
LEADING = 1.25                           # line-height multiplier

FONT_REG = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
TO_FS_MAX, FROM_FS_MAX, ITEM_FS_MAX = 13, 13, 12
FS_MIN = 9                               # don't go below this

# Target vertical allocation (fractions of inner height)
ALLOC_TO, ALLOC_FROM = 0.42, 0.40        # item gets the rest


def wrap_lines(text, font_name, font_size, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if pdfmetrics.stringWidth(trial, font_name, font_size) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text_to_height(text, font_name, fs_max, fs_min, max_width, max_height):
    fs = fs_max
    while fs >= fs_min:
        lines = wrap_lines(text, font_name, fs, max_width) if text.strip() else [""]
        total_h = len(lines) * fs * LEADING
        if total_h <= max_height:
            return fs, lines, total_h
        fs -= 0.5
    # last resort: clip
    return max(fs_min, 6), lines, total_h


def draw_block(c, x, y_top, w, h, text, font_name, fs_max, add_divider=True, bold=False):
    fs, lines, total_h = fit_text_to_height(text, font_name, fs_max, FS_MIN, w, h)
    y = y_top - fs  # baseline
    c.setFont(font_name, fs)
    for ln in lines:
        c.drawString(x, y, ln)
        y -= fs * LEADING
    if add_divider:
        c.setLineWidth(DIVIDER_PT)
        c.line(PAD, y, PAGE_W - PAD, y)
    return y  # returns current y (below block)


def draw_label(c, to_text, from_text, item_text):
    # outer border
    c.setLineWidth(BORDER_PT)
    c.rect(BORDER_PT/2, BORDER_PT/2, PAGE_W - BORDER_PT, PAGE_H - BORDER_PT)

    inner_top = PAGE_H - PAD
    inner_bottom = PAD
    inner_height = inner_top - inner_bottom

    x = PAD
    w = PAGE_W - 2*PAD

    # TO block
    to_h = inner_height * ALLOC_TO
    y = draw_block(c, x, inner_top, w, to_h, to_text, FONT_BOLD, TO_FS_MAX, add_divider=True)

    # FROM block
    from_h = inner_height * ALLOC_FROM
    # small spacing below divider
    y -= 0.08*inch
    y = draw_block(c, x, y, w, from_h, from_text, FONT_REG, FROM_FS_MAX, add_divider=True)

    # ITEM block (rest)
    y -= 0.08*inch
    remaining_h = y - inner_bottom
    draw_block(c, x, y, w, remaining_h, item_text, FONT_REG, ITEM_FS_MAX, add_divider=False)


def generate_label_pdf(input_path, output_folder):
    """
    Reads data from input_path (CSV), generates a PDF in output_folder.
    Returns the filename of the generated PDF.
    """
    # 1. Get Data
    data = fetch_address.get_data(input_path)
    
    # 2. Define Output Path
    # Create a filename based on the input, or just a generic timestamped one.
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_filename = f"LABELS_{base_name}.pdf"
    output_full_path = os.path.join(output_folder, output_filename)

    # 3. Draw PDF
    c = canvas.Canvas(output_full_path, pagesize=(PAGE_W, PAGE_H))
    
    for obj in data:
        to_text = str(obj.get("to", "")).strip()
        from_text = FROM_ADDRESS.strip()
        item_text = str(obj.get("item", "")).strip()
        
        draw_label(c, to_text, from_text, item_text)
        c.showPage()
        
    c.save()
    
    return output_filename

