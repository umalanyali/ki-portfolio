import html
import json
import os
import re
from datetime import date

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from utils.ui import empty_state, hero, source_card

load_dotenv()

MODEL = "gpt-4o-mini"
MAX_RESULTS = 5
RECURSION_LIMIT = 30

SYSTEM_PROMPT = """Du bist ein erfahrener Unternehmensanalyst und KI-Strategieberater.
Heute ist der {today}.

Deine Aufgabe: Recherchiere das angegebene Unternehmen selbstständig mit dem Websuche-Tool
und erstelle anschließend einen strukturierten Analyse-Report.

Vorgehen:
- Führe mehrere gezielte Suchen durch (ca. 4–6), z. B. zu Unternehmensprofil, Produkten,
  Wettbewerbern/Marktposition und aktuellen Nachrichten (nutze für News topic="news").
- Stütze dich ausschließlich auf die Suchergebnisse. Erfinde keine Zahlen oder Fakten.
  Wenn etwas nicht auffindbar ist, schreibe das offen.
- Ist der Firmenname mehrdeutig, wähle das bekannteste passende Unternehmen (berücksichtige
  die Branche, falls angegeben) und erwähne die Annahme kurz.

Antworte am Ende ausschließlich mit dem Report in Markdown, auf Deutsch, in genau dieser Struktur:

## Unternehmensüberblick
(Kurzprofil: Gründung, Sitz, Größe/Mitarbeitende, Umsatz falls bekannt, Rechtsform, Geschäftsmodell)

## Produkte & Dienstleistungen
(Wichtigste Produkte, Services und Zielgruppen als Liste)

## Marktposition
(Branche, Marktstellung, wichtigste Wettbewerber, Stärken und Schwächen – gern als Tabelle)

## Aktuelle News
(3–5 aktuelle Meldungen als Liste, jeweils mit Datum falls bekannt und Quelle als Markdown-Link)

## Mögliche KI-Potenziale
(3–5 konkrete, auf dieses Unternehmen zugeschnittene KI-Anwendungsfälle. Für jeden:
**Titel** – Beschreibung, erwarteter Nutzen, Aufwand (niedrig/mittel/hoch))

## Fazit
(2–3 Sätze Gesamteinschätzung)

Setze Quellen als Markdown-Links direkt an die passenden Stellen im Text."""


def build_agent():
    search = TavilySearch(max_results=MAX_RESULTS, search_depth="advanced")
    llm = ChatOpenAI(model=MODEL, temperature=0.2)
    return create_agent(
        llm,
        tools=[search],
        system_prompt=SYSTEM_PROMPT.format(today=date.today().strftime("%d.%m.%Y")),
    )


def build_request(company: str, industry: str) -> str:
    request = f"Analysiere das Unternehmen: {company}"
    if industry:
        request += f"\nBranche: {industry}"
    return request


def extract_sources(tool_content) -> list[dict]:
    """Liest Titel, URL und Ausschnitt aus der Tavily-Antwort."""
    data = tool_content
    if isinstance(tool_content, str):
        try:
            data = json.loads(tool_content)
        except json.JSONDecodeError:
            return []
    if not isinstance(data, dict):
        return []
    sources = []
    for r in data.get("results", []):
        if not r.get("url"):
            continue
        snippet = " ".join((r.get("content") or "").split())
        sources.append(
            {
                "title": r.get("title") or r["url"],
                "url": r["url"],
                "snippet": snippet[:220] + ("…" if len(snippet) > 220 else ""),
            }
        )
    return sources


def run_analysis(company: str, industry: str, status) -> tuple[str, list[str], list[dict]]:
    """Führt den Agenten aus und zeigt jeden Rechercheschritt live im Status-Container."""
    agent = build_agent()
    queries, sources, report = [], {}, ""

    for update in agent.stream(
        {"messages": [{"role": "user", "content": build_request(company, industry)}]},
        stream_mode="updates",
        config={"recursion_limit": RECURSION_LIMIT},
    ):
        for node_output in update.values():
            for msg in (node_output or {}).get("messages", []):
                if isinstance(msg, AIMessage):
                    for call in msg.tool_calls:
                        query = call["args"].get("query", "")
                        queries.append(query)
                        status.update(label=f"Recherche {len(queries)}: {query}")
                        status.write(f":material/search: **Suche:** {query}")
                    if not msg.tool_calls and msg.content:
                        report = msg.text if hasattr(msg, "text") else str(msg.content)
                elif isinstance(msg, ToolMessage):
                    found = extract_sources(msg.content)
                    for s in found:
                        sources.setdefault(s["url"], s)
                    status.write(f"↳ {len(found)} Ergebnisse gefunden")

    return report.strip(), queries, list(sources.values())


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"Recherchierte Quellen ({len(sources)})", icon=":material/menu_book:"):
        st.html("".join(source_card(s["title"], s["snippet"], s["url"]) for s in sources))


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "unternehmen"


# --- Session State ---
st.session_state.setdefault("analysis", None)

# --- Header ---
hero(
    "building",
    "Unternehmensanalyse",
    "Gib einen Firmennamen ein – der KI-Agent recherchiert selbstständig im Web und erstellt "
    "einen strukturierten Report inklusive KI-Potenzialen.",
    eyebrow="Agent 02 · Web-Recherche",
)

missing = [key for key in ("OPENAI_API_KEY", "TAVILY_API_KEY") if not os.getenv(key)]
if missing:
    st.error(
        f"Fehlende API-Keys: {', '.join(f'`{k}`' for k in missing)}. "
        "Bitte in der `.env`-Datei eintragen und die App neu starten."
    )
    st.stop()

# --- Sidebar: Eingabe ---
with st.sidebar:
    st.header("Unternehmen")
    with st.form("analyse_form"):
        company = st.text_input("Firmenname *", placeholder="z. B. Siemens")
        industry = st.text_input(
            "Branche (optional)",
            placeholder="z. B. Industrieautomatisierung",
            help="Hilft dem Agenten bei mehrdeutigen Firmennamen.",
        )
        submitted = st.form_submit_button("Analyse starten", type="primary", use_container_width=True)

    if st.session_state.analysis:
        st.divider()
        if st.button("Ergebnis löschen", use_container_width=True):
            st.session_state.analysis = None
            st.rerun()

# --- Analyse ausführen ---
if submitted:
    company, industry = company.strip(), industry.strip()
    if not company:
        st.sidebar.warning("Bitte einen Firmennamen eingeben.")
    else:
        with st.status(f"Agent recherchiert zu „{company}“ …", expanded=True) as status:
            try:
                report, queries, sources = run_analysis(company, industry, status)
            except Exception as e:
                status.update(label="Analyse fehlgeschlagen", state="error")
                st.error(f"Es ist ein Fehler aufgetreten: {e}")
            else:
                if report:
                    status.update(
                        label=f"Recherche abgeschlossen · {len(queries)} Suchen · {len(sources)} Quellen",
                        state="complete",
                        expanded=False,
                    )
                    st.session_state.analysis = {
                        "company": company,
                        "industry": industry,
                        "report": report,
                        "sources": sources,
                    }
                else:
                    status.update(label="Kein Report erzeugt", state="error")
                    st.error("Der Agent hat keinen Report geliefert. Bitte erneut versuchen.")

# --- Ergebnis ---
analysis = st.session_state.analysis
if analysis is None:
    empty_state(
        "search",
        "Bereit für die Recherche",
        "Gib links einen Firmennamen ein und klicke auf „Analyse starten“. "
        "Der Agent sucht, liest und fasst die Ergebnisse zusammen.",
    )
    st.stop()

header = f"Analyse: {analysis['company']}"
if analysis["industry"]:
    header += f" · {analysis['industry']}"

with st.container(key="report"):
    chips = [analysis["company"], analysis["industry"], f"{len(analysis['sources'])} Quellen"]
    st.html(
        '<div class="report-meta">'
        + "".join(f'<span class="chip">{html.escape(c)}</span>' for c in chips if c)
        + "</div>"
    )
    st.markdown(analysis["report"])

render_sources(analysis["sources"])

st.download_button(
    "Report als Markdown herunterladen",
    icon=":material/download:",
    data=f"# {header}\n\n{analysis['report']}\n",
    file_name=f"analyse-{slugify(analysis['company'])}.md",
    mime="text/markdown",
)
