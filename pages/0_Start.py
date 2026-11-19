import html

import streamlit as st

from utils.ui import icon

AGENTS = [
    {
        "icon": "file-text",
        "title": "Dokument-Assistent",
        "description": "Stelle Fragen an eigene PDFs und erhalte Antworten mit Seitenquellen.",
        "tag": "RAG · ChromaDB",
        "href": "dokument-assistent",
    },
    {
        "icon": "building",
        "title": "Unternehmensanalyse",
        "description": "Ein Agent recherchiert im Web und erstellt einen strukturierten Report.",
        "tag": "Agent · Tavily",
        "href": "unternehmensanalyse",
    },
    {
        "icon": "gauge",
        "title": "KI-Readiness-Check",
        "description": "Bewerte den KI-Reifegrad eines Unternehmens anhand klarer Kriterien.",
        "tag": "Bald verfügbar",
        "href": "ki-readiness-check",
    },
]

STACK = ["Python", "Streamlit", "LangChain", "LangGraph", "OpenAI", "ChromaDB", "Tavily"]

cards = "".join(
    f"""<a class="glass feature-card" href="{a['href']}">
        <div class="card-icon">{icon(a['icon'], 24)}</div>
        <h3>{html.escape(a['title'])}</h3>
        <p>{html.escape(a['description'])}</p>
        <div class="card-footer"><span class="chip">{html.escape(a['tag'])}</span>
            <span>Öffnen {icon('arrow-right', 16)}</span></div>
    </a>"""
    for a in AGENTS
)

st.html(
    f"""<section class="hero hero--center">
        <div class="hero-icon">{icon('sparkles', 28)}</div>
        <div><span class="eyebrow">KI-Portfolio</span>
            <h1>Drei KI-Agenten für echte Geschäftsfragen</h1>
            <p>Von Dokumenten-Q&amp;A über autonome Webrecherche bis zur KI-Reifegrad-Analyse –
               gebaut mit LangChain und modernen LLMs.</p></div>
    </section>
    <nav class="feature-grid" aria-label="KI-Agenten">{cards}</nav>
    <div class="chip-row">{''.join(f'<span class="chip">{s}</span>' for s in STACK)}</div>"""
)
