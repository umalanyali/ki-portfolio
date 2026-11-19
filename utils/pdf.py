"""Gemeinsame PDF-Basis (fpdf2) für die Reports: Schrift, Farben, Kopf, Fußzeile, Abschnitte, Markdown."""

import re
from datetime import date
from urllib.parse import urlparse

from fpdf import FPDF
from fpdf.fonts import FontFace

AUTHOR_FOOTER = "Erstellt mit KI-Portfolio von Umutcan Alanyali"

BLUE = (0, 113, 227)
TEXT = (29, 29, 31)
GRAY = (110, 110, 115)
LINE = (210, 210, 215)
BG_ALT = (245, 245, 247)

# Helvetica (Core-Font) kann nur Latin-1. Umlaute/ß sind enthalten, typografische Zeichen
# aus LLM-Texten (Gedankenstrich, deutsche Anführungszeichen …) würden fpdf2 abbrechen lassen.
_REPLACEMENTS = str.maketrans(
    {"–": "-", "—": "-", "„": '"', "“": '"', "”": '"', "‚": "'", "‘": "'", "’": "'",
     "…": "...", "•": "-", "→": "->", " ": " ",
     # Inhaltlich wichtige Zeichen ausschreiben statt verwerfen (z. B. Umsatzangaben)
     "€": "EUR", "≈": "ca.", "≤": "<=", "≥": ">=", "™": "(TM)", "‰": " Promille"}
)


def pdf_text(text: str) -> str:
    """Macht Text Latin-1-tauglich; nicht darstellbare Zeichen (z. B. Emojis) werden entfernt."""
    cleaned = str(text).translate(_REPLACEMENTS).encode("latin-1", "ignore").decode("latin-1")
    return re.sub(r"[ \t]{2,}", " ", cleaned).strip()


def pdf_filename(prefix: str, company: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9ÄÖÜäöüß-]+", "-", company).strip("-") or "Unternehmen"
    return f"{prefix}-{safe}-{date.today().isoformat()}.pdf"


def _inline_markdown(text: str) -> str:
    """Entfernt Inline-Markdown; Links werden zu 'Text (domain.de)'."""
    def link(m: re.Match) -> str:
        domain = urlparse(m[2]).netloc.removeprefix("www.")
        return f"{m[1]} ({domain})" if domain and domain not in m[1] else m[1]

    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", link, text)
    text = text.replace("**", "").replace("__", "").replace("`", "")
    return re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", text)


class ReportPDF(FPDF):
    """A4-Dokument im App-Stil: Helvetica, blaue Abschnittstitel, Fußzeile mit Autor und Seitenzahl."""

    def __init__(self, title: str, meta: list[str]):
        super().__init__(format="A4")
        self.set_margins(20, 20, 20)
        self.set_auto_page_break(True, margin=22)
        self.add_page()
        self.write_text(title, size=22, style="B", height=10)
        self.write_text(" · ".join([m for m in meta if m] + [date.today().strftime("%d.%m.%Y")]), size=10, color=GRAY)
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GRAY)
        self.cell(self.epw / 2, 10, AUTHOR_FOOTER, align="L")
        self.cell(self.epw / 2, 10, f"Seite {self.page_no()}/{{nb}}", align="R")

    def write_text(self, text: str, size: float = 10.5, style: str = "", color=TEXT, height: float = 5.5, indent: float = 0) -> None:
        self.set_font("Helvetica", style, size)
        self.set_text_color(*color)
        self.set_x(self.l_margin + indent)
        self.multi_cell(self.epw - indent, height, pdf_text(text), align="L", new_x="LMARGIN", new_y="NEXT")

    def section(self, title: str) -> None:
        self.ln(6)
        self.write_text(title, size=13, style="B", color=BLUE, height=7)
        self.set_draw_color(*LINE)
        self.line(self.l_margin, self.get_y() + 1, self.l_margin + self.epw, self.get_y() + 1)
        self.ln(4)

    def numbered(self, items: list[tuple[str, str]]) -> None:
        for i, (title, text) in enumerate(items, 1):
            self.write_text(f"{i}. {title}", style="B")
            self.write_text(text, color=GRAY)
            self.ln(2)

    def markdown(self, md: str) -> None:
        """Rendert LLM-Markdown als Klartext: ##-Überschriften, Listen, Tabellen, Absätze."""
        table: list[list[str]] = []
        for raw in md.splitlines() + [""]:
            line = raw.strip()
            if line.startswith("|"):
                if not re.fullmatch(r"\|?[\s:|-]+\|?", line):  # Trennzeile |---| überspringen
                    table.append([_inline_markdown(c.strip()) for c in line.strip("|").split("|")])
                continue
            if table:
                self._table(table)
                table = []
            if not line:
                self.ln(1.5)
            elif heading := re.match(r"^(#{1,6})\s+(.*)", line):
                text = _inline_markdown(heading[2])
                if len(heading[1]) <= 2:
                    self.section(text)
                else:
                    self.write_text(text, size=11.5, style="B", height=6.5)
            elif bullet := re.match(r"^[-*+]\s+(.*)", line):
                self.write_text(f"-  {_inline_markdown(bullet[1])}", indent=3)
            elif number := re.match(r"^(\d+)[.)]\s+(.*)", line):
                self.write_text(f"{number[1]}.  {_inline_markdown(number[2])}", indent=3)
            else:
                self.write_text(_inline_markdown(line))

    def _table(self, rows: list[list[str]]) -> None:
        width = max(len(r) for r in rows)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*TEXT)
        self.set_draw_color(*LINE)
        heading = FontFace(emphasis="BOLD", color=TEXT, fill_color=BG_ALT)
        with self.table(text_align="LEFT", line_height=5.5, headings_style=heading, borders_layout="HORIZONTAL_LINES") as table:
            for row in rows:
                cells = table.row()
                for cell in row + [""] * (width - len(row)):
                    cells.cell(pdf_text(cell))
        self.ln(3)

    def to_bytes(self) -> bytes:
        return bytes(self.output())
