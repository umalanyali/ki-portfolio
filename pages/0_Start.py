import html

import streamlit as st

from utils.ui import icon

AGENTS = [
    {
        "icon": "file-text",
        "title": "Dokument-Assistent",
        "description": "Fragen an eigene PDFs stellen – mit Seitenangaben als Quelle.",
        "href": "dokument-assistent",
    },
    {
        "icon": "building",
        "title": "Unternehmensanalyse",
        "description": "Ein Agent recherchiert im Web und schreibt einen strukturierten Report.",
        "href": "unternehmensanalyse",
    },
    {
        "icon": "gauge",
        "title": "KI-Readiness-Check",
        "description": "Den KI-Reifegrad eines Unternehmens anhand klarer Kriterien bewerten.",
        "href": "ki-readiness-check",
    },
]


def card(agent: dict) -> str:
    return (
        f'<a class="card feature-card" href="{agent["href"]}">{icon(agent["icon"], 28)}'
        f'<h3>{html.escape(agent["title"])}</h3><p>{html.escape(agent["description"])}</p>'
        f'<span class="card-link">Öffnen {icon("chevron-right", 14)}</span></a>'
    )


st.html(
    '<section class="home-hero"><h1>KI-Portfolio</h1>'
    "<p>Drei KI-Agenten für echte Geschäftsfragen – von Dokumenten-Q&amp;A bis zur autonomen Webrecherche.</p>"
    "</section>"
    f'<nav class="feature-grid" aria-label="KI-Agenten">{"".join(card(a) for a in AGENTS)}</nav>'
    '<p class="stack-note">Gebaut mit Python, Streamlit, LangChain, OpenAI und Tavily.</p>'
)
