
from pathlib import Path
import re
import html

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
)

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "data" / "processed" / "databricks_newsletter_draft.md"
OUTPUT_FILE = ROOT / "data" / "processed" / "databricks_newsletter.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4

doc = SimpleDocTemplate(
    str(OUTPUT_FILE),
    pagesize=A4,
    leftMargin=0.68 * inch,
    rightMargin=0.68 * inch,
    topMargin=0.75 * inch,
    bottomMargin=0.70 * inch,
    title="AI & Data Weekly",
    author="AI & Data Newsletter Automation",
)

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="NewsletterTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=23,
    leading=29,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#17365D"),
    spaceAfter=10,
))

styles.add(ParagraphStyle(
    name="NewsletterSubtitle",
    parent=styles["Normal"],
    fontSize=10,
    leading=15,
    textColor=colors.HexColor("#555555"),
    spaceAfter=12,
))

styles.add(ParagraphStyle(
    name="SectionHeading",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=20,
    textColor=colors.HexColor("#17365D"),
    spaceBefore=14,
    spaceAfter=8,
    keepWithNext=True,
))

styles.add(ParagraphStyle(
    name="ArticleHeading",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=15,
    textColor=colors.HexColor("#1F4E79"),
    spaceBefore=10,
    spaceAfter=5,
    keepWithNext=True,
))

styles.add(ParagraphStyle(
    name="NewsletterBody",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=14,
    textColor=colors.HexColor("#252525"),
    spaceAfter=7,
    splitLongWords=True,
))

styles.add(ParagraphStyle(
    name="NewsletterBullet",
    parent=styles["NewsletterBody"],
    leftIndent=14,
    firstLineIndent=-8,
    spaceAfter=5,
))


def normalize_markdown(text):
    """Normalize the escaped Markdown found in the current draft."""

    text = text.lstrip("\ufeff")

    # Remove backslashes used to escape Markdown punctuation.
    # Do this before parsing headings, lists, separators and links.
    text = re.sub(r"\\([#*\-_\[\]()!`])", r"\1", text)

    # The provided draft may contain HTML character references
    # inside URLs. Decode those references.
    text = html.unescape(text)

    # Remove redundant blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def inline_markdown(text):
    """Convert bold, italic, code and links to ReportLab markup."""

    placeholders = []

    def save_markup(markup):
        token = f"ZZMARKUP{len(placeholders)}ZZ"
        placeholders.append((token, markup))
        return token

    # Convert Markdown links before escaping other text.
    def replace_link(match):
        label = html.escape(match.group(1))
        url = match.group(2).strip()

        if not url.lower().startswith(("https://", "http://")):
            return html.escape(match.group(0))

        safe_url = html.escape(url, quote=True)

        return save_markup(
            f'<link href="{safe_url}" color="#0563C1">'
            f"<u>{label}</u></link>"
        )

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        replace_link,
        text,
    )

    # Escape normal text so symbols don't break ReportLab markup.
    text = html.escape(text)

    # Inline code.
    text = re.sub(
        r"`([^`]+)`",
        lambda m: save_markup(
            f'<font name="Courier">{html.escape(m.group(1))}</font>'
        ),
        text,
    )

    # Bold and italic formatting.
    text = re.sub(
        r"\*\*(.+?)\*\*",
        lambda m: save_markup(f"<b>{m.group(1)}</b>"),
        text,
    )

    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        lambda m: save_markup(f"<i>{m.group(1)}</i>"),
        text,
    )

    # Restore saved markup.
    for token, markup in placeholders:
        text = text.replace(token, markup)

    return text


def draw_page(canvas, document):
    canvas.saveState()

    canvas.setStrokeColor(colors.HexColor("#D9E2F3"))
    canvas.setLineWidth(0.7)

    canvas.line(
        doc.leftMargin,
        PAGE_HEIGHT - 0.48 * inch,
        PAGE_WIDTH - doc.rightMargin,
        PAGE_HEIGHT - 0.48 * inch,
    )

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(
        doc.leftMargin,
        PAGE_HEIGHT - 0.38 * inch,
        "AI & DATA WEEKLY | DATABRICKS",
    )

    canvas.line(
        doc.leftMargin,
        0.48 * inch,
        PAGE_WIDTH - doc.rightMargin,
        0.48 * inch,
    )

    canvas.drawRightString(
        PAGE_WIDTH - doc.rightMargin,
        0.30 * inch,
        f"Page {document.page}",
    )

    canvas.restoreState()


def build_elements(markdown):
    elements = []
    lines = markdown.splitlines()

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        if line in ("---", "***", "___"):
            elements.append(Spacer(1, 3))
            elements.append(HRFlowable(
                width="100%",
                thickness=0.7,
                color=colors.HexColor("#D9E2F3"),
                spaceBefore=3,
                spaceAfter=7,
            ))
            continue

        if line.startswith("# "):
            elements.append(Paragraph(
                inline_markdown(line[2:].strip()),
                styles["NewsletterTitle"],
            ))
            continue

        if line.startswith("## "):
            elements.append(Paragraph(
                inline_markdown(line[3:].strip()),
                styles["SectionHeading"],
            ))
            continue

        if line.startswith("### "):
            elements.append(Paragraph(
                inline_markdown(line[4:].strip()),
                styles["ArticleHeading"],
            ))
            continue

        if line.startswith("- [ ] "):
            elements.append(Paragraph(
                "&#9744; " + inline_markdown(line[6:].strip()),
                styles["NewsletterBullet"],
            ))
            continue

        if line.lower().startswith("- [x] "):
            elements.append(Paragraph(
                "&#9745; " + inline_markdown(line[6:].strip()),
                styles["NewsletterBullet"],
            ))
            continue

        if line.startswith(("- ", "* ")):
            elements.append(Paragraph(
                "&#8226; " + inline_markdown(line[2:].strip()),
                styles["NewsletterBullet"],
            ))
            continue

        elements.append(Paragraph(
            inline_markdown(line),
            styles["NewsletterBody"],
        ))

    return elements


def main():
    print("=" * 55)
    print("DATABRICKS NEWSLETTER PDF GENERATOR")
    print("=" * 55)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Markdown draft not found: {INPUT_FILE}"
        )

    original_text = INPUT_FILE.read_text(encoding="utf-8")
    markdown = normalize_markdown(original_text)

    elements = build_elements(markdown)

    if not elements:
        raise ValueError(
            "No content was extracted. Check the Markdown draft."
        )

    # Confirm the parser found the expected story headings.
    article_count = sum(
        1 for line in markdown.splitlines()
        if re.match(r"^###\s+\d+\.", line.strip())
    )

    if article_count == 0:
        raise ValueError(
            "No numbered article headings found. "
            "Check the Markdown heading format."
        )

    print(f"Article headings detected: {article_count}")
    print(f"PDF elements generated: {len(elements)}")
    print(f"Input: {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")

    doc.build(
        elements,
        onFirstPage=draw_page,
        onLaterPages=draw_page,
    )

    if not OUTPUT_FILE.exists() or OUTPUT_FILE.stat().st_size == 0:
        raise RuntimeError("PDF output was not created correctly.")

    print("\nPDF generated successfully.")
    print(f"File size: {OUTPUT_FILE.stat().st_size:,} bytes")
    print("Please open and visually review the PDF.")


if __name__ == "__main__":
    main()
