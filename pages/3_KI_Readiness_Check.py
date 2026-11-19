import html
import os
import threading
import time
import unicodedata
from typing import Literal

import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from utils import pdf as pdf_style
from utils.pdf import ReportPDF, pdf_filename, pdf_text
from utils.ui import action_bar, page_header

load_dotenv()

MODEL = "gpt-4o-mini"

# (Kategorie, [(Frage, Anker bei 0, Anker bei 5), ...])
CATEGORIES = [
    (
        "Datenstrategie",
        [
            ("Wie strukturiert sind Ihre Unternehmensdaten?", "gar nicht", "vollständig strukturiert"),
            ("Nutzen Sie bereits Datenanalyse für Entscheidungen?", "nie", "täglich/systematisch"),
        ],
    ),
    (
        "Prozessreife",
        [
            ("Wie digitalisiert sind Ihre Kernprozesse?", "papierbasiert", "volldigital"),
            ("Existieren repetitive Aufgaben die automatisierbar wären?", "keine", "sehr viele"),
        ],
    ),
    (
        "Team & Kompetenz",
        [
            ("Wie hoch ist das KI-Grundwissen im Team?", "kein Wissen", "hohes Wissen"),
            ("Wie offen ist Ihr Team für KI-basierte Arbeitsweisen?", "starker Widerstand", "sehr offen"),
        ],
    ),
    (
        "Führung & Strategie",
        [
            ("Hat KI einen festen Platz in Ihrer Unternehmensstrategie?", "gar nicht", "zentraler Bestandteil"),
            ("Gibt es ein eigenes Budget für KI-Initiativen?", "kein Budget", "festes, ausreichendes Budget"),
        ],
    ),
    (
        "Infrastruktur & IT",
        [
            ("Wie stark nutzen Sie Cloud-Dienste?", "gar nicht", "Cloud-first"),
            ("Wie gut sind Ihre IT-Systeme miteinander integriert?", "isolierte Insellösungen", "vollständig integriert"),
        ],
    ),
]
QUESTIONS = [q for _, qs in CATEGORIES for q in qs]
STEPS = ["Unternehmen"] + [name for name, _ in CATEGORIES]
SCALE = [0, 1, 2, 3, 4, 5]


# --- Bewertung (deterministisch, nicht vom LLM) ---
def total_score(answers: list[int]) -> int:
    return round(sum(answers) / (5 * len(answers)) * 100)


def ampel(score: int) -> tuple[str, str]:
    if score >= 70:
        return "Grün", "green"
    if score >= 40:
        return "Gelb", "amber"
    return "Rot", "red"


def category_scores(answers: list[int]) -> list[tuple[str, int]]:
    """Punkte je Kategorie (0–10)."""
    scores, i = [], 0
    for name, qs in CATEGORIES:
        scores.append((name, sum(answers[i : i + len(qs)])))
        i += len(qs)
    return scores


# --- PDF-Export ---
AMPEL_RGB = {"green": (36, 138, 61), "amber": (178, 80, 0), "red": (215, 0, 21)}


def generate_pdf_report(data: dict) -> bytes:
    """Erzeugt den KI-Readiness-Report als PDF. `data` ist das Ergebnis-Dict aus st.session_state.rc_result."""
    report = data["report"]
    score = total_score(data["answers"])
    status, tone = ampel(score)
    pdf = ReportPDF("KI-Readiness Report", [data["company"], data["industry"]])

    # Score
    pdf.set_font("Helvetica", "B", 34)
    pdf.set_text_color(*AMPEL_RGB[tone])
    pdf.cell(pdf.get_string_width(f"{score} "), 14, f"{score} ")
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(*pdf_style.GRAY)
    pdf.cell(0, 16, "/ 100", new_x="LMARGIN", new_y="NEXT")
    pdf.write_text(f"Ampel-Status: {status}", size=11, style="B", color=AMPEL_RGB[tone])

    # Kategorien als Tabelle mit Balken
    pdf.section("Ergebnis nach Kategorie")
    col_name, col_score = 70, 20
    bar_width = pdf.epw - col_name - col_score
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*pdf_style.GRAY)
    pdf.cell(col_name, 7, "KATEGORIE")
    pdf.cell(col_score, 7, "SCORE", new_x="LMARGIN", new_y="NEXT")
    for name, pts in category_scores(data["answers"]):
        y = pdf.get_y()
        pdf.set_font("Helvetica", "", 10.5)
        pdf.set_text_color(*pdf_style.TEXT)
        pdf.cell(col_name, 8, pdf_text(name))
        pdf.cell(col_score, 8, f"{pts}/10")
        bar_x, bar_y = pdf.get_x(), y + 3
        pdf.set_fill_color(*pdf_style.BG_ALT)
        pdf.rect(bar_x, bar_y, bar_width, 2.2, style="F")
        if pts:
            pdf.set_fill_color(*pdf_style.BLUE)
            pdf.rect(bar_x, bar_y, bar_width * pts / 10, 2.2, style="F")
        pdf.ln(8)
        pdf.set_draw_color(*pdf_style.LINE)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + pdf.epw, pdf.get_y())

    pdf.section("Zusammenfassung")
    pdf.write_text(report.zusammenfassung)
    pdf.section("Stärken")
    pdf.numbered([(p.titel, p.beschreibung) for p in report.staerken])
    pdf.section("Handlungsfelder")
    pdf.numbered([(p.titel, p.beschreibung) for p in report.handlungsfelder])
    pdf.section("Empfehlungen")
    order = {"Hoch": 0, "Mittel": 1, "Niedrig": 2}
    recs = sorted(report.empfehlungen, key=lambda r: order[r.prioritaet])
    pdf.numbered([(f"{r.titel}  (Priorität: {r.prioritaet})", r.beschreibung) for r in recs])
    pdf.section("Zeithorizont")
    pdf.write_text(report.zeithorizont, size=13, style="B", height=7)
    pdf.write_text(f"bis zu ersten KI-Ergebnissen. {report.zeithorizont_begruendung}", color=pdf_style.GRAY)
    pdf.ln(6)
    pdf.write_text(
        "Score = Summe der 10 Antworten (je 0-5), skaliert auf 100. Ampel: unter 40 Rot, 40-69 Gelb, ab 70 Grün.",
        size=8.5,
        color=pdf_style.GRAY,
    )
    return pdf.to_bytes()


# --- LLM-Report ---
class Punkt(BaseModel):
    titel: str = Field(description="Kurze Überschrift, max. 6 Wörter")
    beschreibung: str = Field(description="1–2 Sätze, konkret auf das Unternehmen bezogen")


class Empfehlung(BaseModel):
    titel: str = Field(description="Konkrete Maßnahme, max. 8 Wörter")
    beschreibung: str = Field(description="2–3 Sätze: was genau, warum, erster Schritt")
    prioritaet: Literal["Hoch", "Mittel", "Niedrig"]


class ReadinessReport(BaseModel):
    zusammenfassung: str = Field(description="2–3 Sätze Gesamteinschätzung")
    staerken: list[Punkt] = Field(description="Genau 3 größte Stärken")
    handlungsfelder: list[Punkt] = Field(description="Genau 3 größte Handlungsfelder")
    empfehlungen: list[Empfehlung] = Field(description="Genau 5 Empfehlungen, nach Priorität sortiert")
    zeithorizont: str = Field(description="Geschätzter Zeitraum bis zu ersten KI-Ergebnissen, z. B. '3–6 Monate'")
    zeithorizont_begruendung: str = Field(description="1–2 Sätze Begründung des Zeithorizonts")


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Du bist eine erfahrene KI-Transformationsberaterin für den deutschen Mittelstand. "
            "Du erstellst auf Basis eines Self-Assessments einen ehrlichen, konkreten "
            "KI-Readiness-Report auf Deutsch (Sie-Form).\n\n"
            "Regeln:\n"
            "- Score und Ampel-Status sind bereits berechnet. Übernimm sie und begründe "
            "deine Einschätzung konsistent dazu – berechne sie nicht neu.\n"
            "- Stärken leiten sich aus hoch bewerteten Antworten ab, Handlungsfelder aus niedrig bewerteten.\n"
            "- Viele automatisierbare repetitive Aufgaben sind ein Potenzial (Quick-Win-Kandidaten).\n"
            "- Empfehlungen müssen zur Branche passen, umsetzbar sein und mit dem nächsten konkreten "
            "Schritt beginnen. Keine Allgemeinplätze wie 'KI-Strategie entwickeln' ohne Details.\n"
            "- Priorität 'Hoch' nur für Maßnahmen, die Voraussetzung für alles Weitere sind oder "
            "schnellen Nutzen bringen.\n"
            "- Der Zeithorizont muss zum Reifegrad passen (niedriger Score = länger).",
        ),
        (
            "human",
            "Unternehmen: {company}\nBranche: {industry}\n"
            "KI-Readiness-Score: {score}/100 (Ampel: {ampel})\n\n"
            "Punkte je Kategorie (0–10):\n{categories}\n\n"
            "Einzelantworten (Skala 0–5):\n{answers}",
        ),
    ]
)


def generate_report(company: str, industry: str, answers: list[int]) -> ReadinessReport:
    score = total_score(answers)
    llm = ChatOpenAI(model=MODEL, temperature=0.3).with_structured_output(ReadinessReport)
    chain = PROMPT | llm
    return chain.invoke(
        {
            "company": company,
            "industry": industry or "nicht angegeben",
            "score": score,
            "ampel": ampel(score)[0],
            "categories": "\n".join(f"- {name}: {pts}/10" for name, pts in category_scores(answers)),
            "answers": "\n".join(
                f"- {q} → {a} (0 = {low}, 5 = {high})" for (q, low, high), a in zip(QUESTIONS, answers)
            ),
        }
    )


# --- Darstellung ---
def esc(text: str) -> str:
    return html.escape(text)


def score_row(result: dict) -> str:
    """Score-Zeile für den sticky Kopf: zählt per CSS von 0 bis zum Score hoch, Farbe läuft mit.

    Streamlit führt <script> in st.markdown/st.html nicht aus – daher eine reine CSS-Animation
    (registrierte Custom Property --rc-n, siehe utils/ui.py). Keyframes je Score, damit das Ziel stimmt.
    """
    score = total_score(result["answers"])
    status, tone = ampel(score)
    return (
        f"<style>@keyframes rc-count-{score} {{ from {{ --rc-n: 0; }} to {{ --rc-n: {score}; }} }}"
        f".rc-count {{ animation-name: rc-count-{score}; }}"
        f"@media (prefers-reduced-motion: reduce) {{ .rc-count {{ --rc-n: {score}; }} }}</style>"
        f'<div class="rc-score-row"><div class="rc-score-value">'
        f'<span class="rc-count" aria-hidden="true"></span><span class="sr-only">{score} von 100 Punkten</span>'
        f'<span class="rc-score-max rc-after-count">/100</span></div>'
        f'<span class="rc-status rc-status-{tone} rc-after-count"><span class="rc-dot"></span>'
        f"KI-Readiness: {status}</span></div>"
    )


# --- Ladeanimation: ASCII-Roboter, während das LLM im Hintergrund-Thread arbeitet ---
ROBOT_FRAMES_RAW = [
    """
╔══════════════════════════════╗
║                              ║
║   ┌─────────┐                ║
║   │ ◉     ◉ │   Analysiere  ║
║   │    ▽    │   Daten...    ║
║   └────┬────┘                ║
║        │                     ║
║   ┌────┴────┐    📄 📄       ║
║   │         │  📄   📄      ║
║   └────┬────┘                ║
║       / \\                    ║
╚══════════════════════════════╝""",
    """
╔══════════════════════════════╗
║                              ║
║   ┌─────────┐                ║
║   │ ◉     ◉ │   Sortiere    ║
║   │    ▽    │   Infos...    ║
║   └────┬────┘                ║
║       /│                     ║
║   ┌───┘ ────┐    📄          ║
║   │    ✋   │  📄            ║
║   └────┬────┘                ║
║       / \\                    ║
╚══════════════════════════════╝""",
    """
╔══════════════════════════════╗
║                              ║
║   ┌─────────┐                ║
║   │ ◉     ◉ │   Erstelle    ║
║   │    ◡    │   Report...   ║
║   └────┬────┘                ║
║   \\    │    /                ║
║   ┌────┴────┐                ║
║   │ 📄📄📄  │                ║
║   └────┬────┘                ║
║       / \\                    ║
╚══════════════════════════════╝""",
    """
╔══════════════════════════════╗
║                              ║
║   ┌─────────┐                ║
║   │ ◉     ◉ │   Fast        ║
║   │    ◡    │   fertig!     ║
║   └────┬────┘                ║
║        │  \\👍                ║
║   ┌────┴────┐                ║
║   │ ✅📋✅  │                ║
║   └────┬────┘                ║
║       / \\                    ║
╚══════════════════════════════╝""",
]
FRAME_DELAY = 0.3


def _display_width(text: str) -> int:
    """Breite in Monospace-Zellen: Emojis/breite Zeichen zählen doppelt."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 0 if unicodedata.combining(c) else 1 for c in text)


# Emojis sind in der Monospace-Schrift ~2,14 Zellen breit (gemessen) – der Rahmen würde ausfransen.
# Ersatz: 1-Zellen-Symbol + Leerzeichen = exakt 2 Zellen, damit Roboter-Kästen und Rahmen bündig bleiben.
_MONO_SAFE = str.maketrans({"📄": "▤ ", "✋": "▪ ", "👍": "✓ ", "✅": "✓ ", "📋": "▦ "})


def _align_frames(frames: list[str]) -> list[str]:
    """Bringt alle Zeilen auf dieselbe sichtbare Breite, damit der rechte Rahmen bündig bleibt."""
    frames = [f.translate(_MONO_SAFE) for f in frames]
    bodies = [[line[1:].rstrip().removesuffix("║").rstrip() for line in f.strip("\n").splitlines()[1:-1]] for f in frames]
    width = max(_display_width(line) for body in bodies for line in body) + 2
    return [
        "\n".join(
            ["╔" + "═" * width + "╗"]
            + ["║" + line + " " * (width - _display_width(line)) + "║" for line in body]
            + ["╚" + "═" * width + "╝"]
        )
        for body in bodies
    ]


ROBOT_FRAMES = _align_frames(ROBOT_FRAMES_RAW)


def run_with_robot(slot, fn, *args):
    """Führt fn(*args) im Hintergrund-Thread aus und animiert solange den Roboter in `slot` (st.empty).

    Der Thread ruft nur LangChain auf – keine st.*-Aufrufe, denn die sind nur im Haupt-Thread erlaubt.
    """
    outcome = {"value": None, "error": None}

    def worker() -> None:
        try:
            outcome["value"] = fn(*args)
        except Exception as e:  # wird im Haupt-Thread angezeigt
            outcome["error"] = e

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    with slot.container(key="rc-loading"):
        # Blur auf Fragebogen und Kopf, solange der Roboter sichtbar ist (verschwindet mit dem Container)
        st.html(
            "<style>.st-key-rc-step, .st-key-page-header, "
            '[class*="st-key-action-bar"] [data-testid="stHorizontalBlock"] '
            "{ filter: blur(8px); pointer-events: none; transition: filter .3s ease; }</style>"
        )
        frame_slot = st.empty()
        st.caption("KI analysiert Ihre Antworten...")
        frame = 0
        while thread.is_alive():
            frame_slot.code(ROBOT_FRAMES[frame % len(ROBOT_FRAMES)], language=None)
            frame += 1
            thread.join(timeout=FRAME_DELAY)  # endet sofort, sobald das LLM fertig ist
    slot.empty()
    if outcome["error"]:
        raise outcome["error"]
    return outcome["value"]


def render_report_body(result: dict) -> None:
    report: ReadinessReport = result["report"]

    def points(title: str, items: list[Punkt]) -> str:
        cards = "".join(
            f'<div class="card rc-point"><h3>{esc(p.titel)}</h3><p>{esc(p.beschreibung)}</p></div>' for p in items
        )
        return f'<h2 class="rc-section">{title}</h2><div class="rc-grid">{cards}</div>'

    bars = "".join(
        f'<div class="rc-cat"><span>{esc(name)}</span>'
        f'<div class="rc-bar"><div class="rc-bar-fill" style="width:{pts * 10}%"></div></div>'
        f'<span class="rc-cat-value">{pts}/10</span></div>'
        for name, pts in category_scores(result["answers"])
    )
    order = {"Hoch": 0, "Mittel": 1, "Niedrig": 2}
    recs = "".join(
        f'<div class="card rc-rec"><div class="rc-rec-head"><h3>{esc(r.titel)}</h3>'
        f'<span class="rc-badge rc-badge-{r.prioritaet.lower()}">{r.prioritaet}</span></div>'
        f"<p>{esc(r.beschreibung)}</p></div>"
        for r in sorted(report.empfehlungen, key=lambda r: order[r.prioritaet])
    )
    st.html(
        f'<p class="rc-summary">{esc(report.zusammenfassung)}</p>'
        f'<h2 class="rc-section">Ergebnis nach Kategorie</h2><div class="card rc-cats">{bars}</div>'
        + points("Stärken", report.staerken)
        + points("Handlungsfelder", report.handlungsfelder)
        + f'<h2 class="rc-section">Empfehlungen</h2><div class="rc-recs">{recs}</div>'
        + f'<h2 class="rc-section">Zeithorizont</h2><div class="card rc-time">'
        f'<div class="rc-time-value">{esc(report.zeithorizont)}</div>'
        f"<p>bis zu ersten KI-Ergebnissen. {esc(report.zeithorizont_begruendung)}</p></div>"
        + '<p class="rc-note">Score = Summe der 10 Antworten (je 0–5), skaliert auf 100. '
        "Ampel: unter 40 Rot, 40–69 Gelb, ab 70 Grün.</p>"
    )

    with st.expander("Bericht kopieren", icon=":material/content_copy:"):
        st.code(report_markdown(result), language="markdown", wrap_lines=True)


def report_markdown(result: dict) -> str:
    report: ReadinessReport = result["report"]
    score = total_score(result["answers"])
    lines = [
        f"# KI-Readiness-Report: {result['company']}",
        f"Branche: {result['industry'] or 'nicht angegeben'}",
        "",
        f"**KI-Readiness-Score: {score} / 100 – Ampel: {ampel(score)[0]}**",
        "",
        report.zusammenfassung,
        "",
        "## Ergebnis nach Kategorie",
        *[f"- {name}: {pts}/10" for name, pts in category_scores(result["answers"])],
        "",
        "## Stärken",
        *[f"- **{p.titel}** – {p.beschreibung}" for p in report.staerken],
        "",
        "## Handlungsfelder",
        *[f"- **{p.titel}** – {p.beschreibung}" for p in report.handlungsfelder],
        "",
        "## Empfehlungen",
        *[f"{i}. **[{r.prioritaet}] {r.titel}** – {r.beschreibung}" for i, r in enumerate(report.empfehlungen, 1)],
        "",
        "## Zeithorizont",
        f"{report.zeithorizont} bis zu ersten KI-Ergebnissen. {report.zeithorizont_begruendung}",
    ]
    return "\n".join(lines)


# --- Navigation ---
def go(delta: int) -> None:
    st.session_state.rc_step += delta


def edit_answers() -> None:
    st.session_state.rc_result = None
    st.session_state.rc_step = len(STEPS) - 1


def reset() -> None:
    for key in [k for k in st.session_state if k.startswith("rc_")]:
        del st.session_state[key]


def answers() -> list[int | None]:
    return [st.session_state.get(f"rc_q{i}") for i in range(len(QUESTIONS))]


# Widget-Werte bleiben erhalten, auch wenn ihr Schritt gerade nicht angezeigt wird.
for key in [k for k in st.session_state if k.startswith(("rc_q", "rc_company", "rc_industry"))]:
    st.session_state[key] = st.session_state[key]
st.session_state.setdefault("rc_step", 0)
st.session_state.setdefault("rc_result", None)

DESCRIPTION = (
    "Zehn Fragen in fünf Kategorien – danach erhalten Sie einen Score und einen "
    "persönlichen KI-Transformationsplan mit konkreten Empfehlungen."
)

# --- Ergebnisansicht: Score oben fixiert, Bericht scrollt, Aktionen unten fixiert ---
if result := st.session_state.rc_result:
    meta = " · ".join(x for x in (result["company"], result["industry"]) if x)
    header = page_header("KI-Readiness-Check", f"Ihr Ergebnis – {meta}", label="Agent 03")
    header.html(score_row(result))
    render_report_body(result)
    with action_bar():
        _, col_edit, col_new, col_pdf = st.columns([1, 1, 1, 1])
        col_edit.button("Antworten bearbeiten", on_click=edit_answers, use_container_width=True)
        col_new.button("Neuer Check", on_click=reset, use_container_width=True)
        col_pdf.download_button(
            label="Als PDF speichern",
            data=generate_pdf_report(result),
            file_name=pdf_filename("KI-Readiness", result["company"]),
            mime="application/pdf",
            type="primary",
            icon=":material/download:",
            use_container_width=True,
        )
    st.stop()

# --- Fragebogen ---
step = st.session_state.rc_step
header = page_header("KI-Readiness-Check", DESCRIPTION, label="Agent 03")
header.progress(step / (len(STEPS) - 1), text=f"Schritt {step + 1} von {len(STEPS)} · {STEPS[step]}")

with st.container(key="rc-step"):
    if step == 0:
        st.html('<h2 class="rc-step-title">Über Ihr Unternehmen</h2>')
        st.text_input("Firmenname *", key="rc_company", placeholder="z. B. Müller Maschinenbau GmbH")
        st.text_input("Branche", key="rc_industry", placeholder="z. B. Maschinenbau")
        step_valid = bool(st.session_state.get("rc_company", "").strip())
        hint_text = "Bitte geben Sie einen Firmennamen ein."
    else:
        name, qs = CATEGORIES[step - 1]
        offset = sum(len(c[1]) for c in CATEGORIES[: step - 1])
        st.html(f'<h2 class="rc-step-title">{esc(name)}</h2>')
        for j, (question, low, high) in enumerate(qs):
            anchors = {0: f"0 · {low}", 5: f"5 · {high}"}
            st.radio(
                question,
                SCALE,
                index=None,
                horizontal=True,
                key=f"rc_q{offset + j}",
                format_func=lambda v, a=anchors: a.get(v, str(v)),
            )
        step_valid = all(st.session_state.get(f"rc_q{offset + j}") is not None for j in range(len(qs)))
        hint_text = "Bitte beantworten Sie beide Fragen."

last_step = step == len(STEPS) - 1
with action_bar():
    hint = st.empty()
    col_back, _, col_next = st.columns([1, 2, 1])
    if step > 0:
        col_back.button("Zurück", on_click=go, args=(-1,), use_container_width=True)

    if not last_step:
        if col_next.button("Weiter", type="primary", use_container_width=True):
            if step_valid:
                go(1)
                st.rerun()
            hint.warning(hint_text)
    elif col_next.button("Analyse starten", type="primary", use_container_width=True):
        if not step_valid or None in answers():
            hint.warning("Bitte beantworten Sie alle Fragen.")
        elif not os.getenv("OPENAI_API_KEY"):
            hint.error("Kein OpenAI API-Key gefunden. Bitte `OPENAI_API_KEY` in der `.env`-Datei eintragen.")
        else:
            company = st.session_state.rc_company.strip()
            industry = st.session_state.get("rc_industry", "").strip()
            try:
                report = run_with_robot(hint, generate_report, company, industry, answers())
            except Exception as e:
                hint.error(f"Die Analyse ist fehlgeschlagen: {e}")
            else:
                st.session_state.rc_result = {
                    "company": company,
                    "industry": industry,
                    "answers": answers(),
                    "report": report,
                }
                st.rerun()
