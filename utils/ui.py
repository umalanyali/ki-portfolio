"""Gemeinsames Design-System der App: Tokens, globales CSS und wiederverwendbare Bausteine.

Farben/Schrift für native Widgets kommen aus .streamlit/config.toml; dieses Modul ergänzt
Glassmorphism-Karten, Hero-Header, Chat-Bubbles und Hover-States. Icons sind Lucide-SVGs.
"""

import html
from urllib.parse import quote

import streamlit as st

_ICON_PATHS = {
    "file-text": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
    '<path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "building": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/>'
    '<path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/>'
    '<path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
    "gauge": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    "sparkles": '<path d="M9.94 15.5A2 2 0 0 0 8.5 14.06l-6.14-1.58a.5.5 0 0 1 0-.96L8.5 9.94A2 2 0 0 0 9.94 8.5'
    'l1.58-6.14a.5.5 0 0 1 .96 0L14.06 8.5A2 2 0 0 0 15.5 9.94l6.14 1.58a.5.5 0 0 1 0 .96L15.5 14.06'
    'a2 2 0 0 0-1.44 1.44l-1.58 6.14a.5.5 0 0 1-.96 0z"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>'
    '<path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
}


_ICON_SIZES = (16, 24, 28)


def icon(name: str, size: int = 24) -> str:
    """Dekoratives Icon. st.html entfernt Inline-<svg>, daher als CSS-Maske (färbt sich per currentColor)."""
    if name not in _ICON_PATHS or size not in _ICON_SIZES:
        raise ValueError(f"Unbekanntes Icon/Größe: {name}/{size}")
    return f'<span class="ui-icon ui-icon-{size} i-{name}" aria-hidden="true"></span>'


def _icon_css() -> str:
    rules = [
        ".ui-icon { display: inline-block; flex: none; vertical-align: -0.2em; background-color: currentColor;"
        " -webkit-mask: var(--icon) center / contain no-repeat; mask: var(--icon) center / contain no-repeat; }"
    ]
    rules += [f".ui-icon-{s} {{ width: {s}px; height: {s}px; }}" for s in _ICON_SIZES]
    for name, paths in _ICON_PATHS.items():
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>'
        )
        rules.append(f'.i-{name} {{ --icon: url("data:image/svg+xml,{quote(svg)}"); }}')
    return "\n".join(rules)


_CSS = """
<style>
:root {
  --bg: #0f1117;
  --surface: rgba(23, 28, 39, 0.62);
  --surface-hover: rgba(30, 36, 51, 0.78);
  --border: rgba(148, 163, 184, 0.14);
  --border-strong: rgba(165, 180, 252, 0.45);
  --text: #e6e9f2;
  --muted: #9aa3b5;
  --accent: #a5b4fc;
  --grad: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  --grad-soft: linear-gradient(135deg, rgba(59, 130, 246, 0.18), rgba(139, 92, 246, 0.18));
  --glow: 0 18px 40px -18px rgba(124, 58, 237, 0.55);
  --radius: 16px;
  --blur: blur(16px);
  --ease: cubic-bezier(0.2, 0.8, 0.2, 1);
}

/* ---------- Fläche & Typografie ---------- */
.stApp {
  background:
    radial-gradient(1100px 560px at 8% -12%, rgba(59, 130, 246, 0.13), transparent 60%),
    radial-gradient(900px 520px at 100% 0%, rgba(139, 92, 246, 0.12), transparent 60%),
    var(--bg);
}
.stApp, .stApp p, .stApp li { font-feature-settings: "cv11", "ss01"; }
.stApp p, .stApp li { line-height: 1.65; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] { max-width: 1180px; padding-top: 2.5rem; padding-bottom: 4rem; }
[data-testid="stAppDeployButton"] { display: none; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { border-right: 1px solid var(--border); }
[data-testid="stSidebarNav"] a {
  border-radius: 10px;
  transition: background-color .2s var(--ease), color .2s var(--ease);
}
[data-testid="stSidebarNav"] a:hover { background: rgba(129, 140, 248, 0.10); }
[data-testid="stSidebarNav"] a[aria-current="page"] {
  background: var(--grad-soft);
  box-shadow: inset 0 0 0 1px rgba(129, 140, 248, 0.25);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
  font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted);
}

/* ---------- Hero ---------- */
.hero {
  display: flex; align-items: flex-start; gap: 1.25rem;
  padding: 0 0 1.75rem; margin-bottom: 1.75rem;
  border-bottom: 1px solid var(--border);
  animation: fade-up .45s var(--ease) both;
}
.hero--center { flex-direction: column; align-items: center; text-align: center; border-bottom: 0; padding: 1.5rem 0 1rem; }
.hero-icon {
  flex: none; display: grid; place-items: center;
  width: 56px; height: 56px; border-radius: 16px;
  background: var(--grad); color: #fff; box-shadow: var(--glow);
}
.eyebrow {
  display: inline-block; font-size: .75rem; font-weight: 600; letter-spacing: .1em;
  text-transform: uppercase; color: var(--accent); margin-bottom: .35rem;
}
.hero h1 {
  font-size: clamp(1.9rem, 3.2vw, 2.6rem); font-weight: 800; letter-spacing: -0.025em;
  line-height: 1.1; margin: 0; padding: 0;
  background: linear-gradient(135deg, #ffffff 35%, #c4b5fd 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero--center h1 { font-size: clamp(2.2rem, 5vw, 3.4rem); }
.hero p { color: var(--muted); font-size: 1.05rem; margin: .6rem 0 0; max-width: 680px; }

/* ---------- Glass-Karten ---------- */
.glass {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
}
.feature-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.25rem; margin-top: 1.5rem; }
@media (max-width: 900px) { .feature-grid { grid-template-columns: 1fr; } }
.feature-card {
  display: flex; flex-direction: column; gap: .9rem; padding: 1.75rem;
  text-decoration: none !important; color: var(--text) !important; cursor: pointer;
  transition: transform .25s var(--ease), border-color .25s var(--ease), box-shadow .25s var(--ease), background-color .25s var(--ease);
  animation: fade-up .5s var(--ease) both;
}
.feature-card:nth-child(2) { animation-delay: .06s; }
.feature-card:nth-child(3) { animation-delay: .12s; }
.feature-card:hover { transform: translateY(-4px); border-color: var(--border-strong); box-shadow: var(--glow); background: var(--surface-hover); }
.feature-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
.feature-card .card-icon {
  display: grid; place-items: center; width: 48px; height: 48px; border-radius: 14px;
  background: var(--grad-soft); border: 1px solid rgba(129, 140, 248, .25); color: #c4b5fd;
}
.feature-card h3 { font-size: 1.15rem; font-weight: 700; margin: 0; padding: 0; color: var(--text); }
.feature-card p { color: var(--muted); margin: 0; font-size: .95rem; }
.card-footer {
  margin-top: auto; padding-top: .5rem; display: flex; align-items: center; justify-content: space-between;
  font-size: .85rem; font-weight: 600; color: var(--accent);
}
.card-footer .ui-icon { transition: transform .25s var(--ease); }
.feature-card:hover .card-footer .ui-icon { transform: translateX(4px); }
.chip {
  display: inline-flex; align-items: center; padding: .2rem .6rem; border-radius: 999px;
  font-size: .72rem; font-weight: 600; color: var(--muted);
  background: rgba(148, 163, 184, .08); border: 1px solid var(--border);
}
.chip-row { display: flex; flex-wrap: wrap; gap: .5rem; justify-content: center; margin-top: 2.5rem; }

/* ---------- Leerer Zustand ---------- */
.empty-state { text-align: center; padding: 3rem 1.5rem; animation: fade-up .45s var(--ease) both; }
.empty-state .card-icon {
  display: inline-grid; place-items: center; width: 52px; height: 52px; border-radius: 16px;
  background: var(--grad-soft); border: 1px solid rgba(129, 140, 248, .25); color: #c4b5fd; margin-bottom: 1rem;
}
.empty-state h3 { font-size: 1.15rem; font-weight: 700; margin: 0 0 .35rem; padding: 0; }
.empty-state p { color: var(--muted); margin: 0 auto; max-width: 460px; }

/* ---------- Buttons ---------- */
button[kind="primary"], button[kind="primaryFormSubmit"] {
  background: var(--grad) !important; border: 0 !important; color: #fff !important; font-weight: 600;
  box-shadow: 0 8px 22px -10px rgba(124, 58, 237, .7);
  transition: transform .2s var(--ease), box-shadow .2s var(--ease), filter .2s var(--ease);
}
button[kind="primary"]:hover:not(:disabled), button[kind="primaryFormSubmit"]:hover:not(:disabled) {
  transform: translateY(-1px); filter: brightness(1.1); box-shadow: 0 12px 28px -10px rgba(124, 58, 237, .85);
}
button[kind="primary"]:active, button[kind="primaryFormSubmit"]:active { transform: translateY(0); }
button[kind="primary"]:disabled, button[kind="primaryFormSubmit"]:disabled { opacity: .45; box-shadow: none; }
button[kind="secondary"], [data-testid="stDownloadButton"] button {
  background: var(--surface) !important; border: 1px solid var(--border) !important;
  transition: border-color .2s var(--ease), background-color .2s var(--ease);
}
button[kind="secondary"]:hover, [data-testid="stDownloadButton"] button:hover {
  border-color: var(--border-strong) !important; background: var(--surface-hover) !important;
}
.stApp button:focus-visible { outline: 2px solid var(--accent) !important; outline-offset: 2px; }

/* ---------- Eingaben ---------- */
[data-baseweb="input"], [data-baseweb="textarea"] { transition: border-color .2s var(--ease), box-shadow .2s var(--ease); }
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
  border-color: #818cf8 !important; box-shadow: 0 0 0 3px rgba(129, 140, 248, .22);
}
[data-testid="stForm"] { border: 1px solid var(--border); background: var(--surface); border-radius: var(--radius); }
[data-testid="stFileUploaderDropzone"] {
  background: var(--surface); border: 1px dashed rgba(148, 163, 184, .3); border-radius: 14px;
  transition: border-color .2s var(--ease), background-color .2s var(--ease);
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--border-strong); background: var(--surface-hover); }

/* ---------- Expander / Status ---------- */
[data-testid="stExpander"] details {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
}
[data-testid="stExpander"] summary { transition: color .2s var(--ease); }
[data-testid="stExpander"] summary:hover { color: var(--accent); }

/* ---------- Chat-Bubbles ---------- */
[data-testid="stChatMessage"] {
  width: fit-content; max-width: min(88%, 860px); gap: .75rem;
  padding: 1rem 1.25rem; margin-bottom: .75rem;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 20px 20px 20px 6px;
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  animation: fade-up .3s var(--ease) both;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  flex-direction: row-reverse; margin-left: auto;
  background: var(--grad); border-color: transparent;
  border-radius: 20px 20px 6px 20px;
  box-shadow: 0 10px 26px -14px rgba(124, 58, 237, .8);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) * { color: #fff; }
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
  border-radius: 10px; width: 2rem; height: 2rem;
}
[data-testid="stChatMessageAvatarAssistant"] { background: var(--grad); color: #fff; }
[data-testid="stChatMessageAvatarUser"] { background: rgba(255, 255, 255, .18); color: #fff; }
[data-testid="stChatMessageContent"] { min-width: 0; }
[data-testid="stChatInput"] > div {
  background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 16px !important;
  backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease);
}
[data-testid="stChatInput"] > div:focus-within { border-color: #818cf8 !important; box-shadow: 0 0 0 3px rgba(129, 140, 248, .2); }

/* ---------- Quellen ---------- */
.source-card {
  display: flex; gap: .75rem; padding: .75rem .9rem; margin-bottom: .5rem;
  background: rgba(129, 140, 248, .06); border: 1px solid var(--border); border-radius: 12px;
  transition: border-color .2s var(--ease), background-color .2s var(--ease);
}
.source-card:hover { border-color: var(--border-strong); background: rgba(129, 140, 248, .1); }
.source-card .source-icon { flex: none; color: var(--accent); margin-top: .1rem; }
.source-card .source-title { font-weight: 600; font-size: .9rem; margin-bottom: .2rem; }
.source-card .source-title a { color: var(--text) !important; text-decoration: none; }
.source-card .source-title a:hover { color: var(--accent) !important; text-decoration: underline; }
.source-card .source-snippet { color: var(--muted); font-size: .84rem; line-height: 1.5; }

/* ---------- Report ---------- */
.st-key-report {
  background: var(--surface); border: 1px solid var(--border); border-radius: 20px;
  padding: 2rem 2.25rem; backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
  animation: fade-up .45s var(--ease) both;
}
.st-key-report h2 {
  font-size: 1.25rem; font-weight: 700; margin-top: 1.75rem; padding: 0 0 0 .8rem;
  border-left: 3px solid; border-image: var(--grad) 1;
}
.st-key-report h2:first-of-type { margin-top: .25rem; }
.st-key-report table { width: 100%; border-collapse: collapse; font-size: .92rem; }
.st-key-report th { background: rgba(129, 140, 248, .12); text-align: left; }
.st-key-report th, .st-key-report td { padding: .6rem .8rem; border: 1px solid var(--border); }
.report-meta { display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: 1.25rem; }

/* ---------- Bewegung ---------- */
@keyframes fade-up { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
</style>
"""


def apply_theme() -> None:
    st.html(_CSS.replace("</style>", _icon_css() + "\n</style>"))


def hero(icon_name: str, title: str, description: str, eyebrow: str = "") -> None:
    eyebrow_html = f'<span class="eyebrow">{html.escape(eyebrow)}</span>' if eyebrow else ""
    st.html(
        f"""<section class="hero">
            <div class="hero-icon">{icon(icon_name, 28)}</div>
            <div>{eyebrow_html}<h1>{html.escape(title)}</h1><p>{html.escape(description)}</p></div>
        </section>"""
    )


def empty_state(icon_name: str, title: str, text: str) -> None:
    st.html(
        f"""<div class="glass empty-state">
            <div class="card-icon">{icon(icon_name, 24)}</div>
            <h3>{html.escape(title)}</h3><p>{html.escape(text)}</p>
        </div>"""
    )


def source_card(title: str, snippet: str, url: str | None = None) -> str:
    """HTML einer Quellenkarte; mit `url` wird der Titel zum externen Link."""
    title_html = html.escape(title)
    if url:
        title_html = f'<a href="{html.escape(url, quote=True)}" rel="noopener">{title_html}</a>'
    return (
        f'<div class="source-card"><span class="source-icon">{icon("link" if url else "file-text", 16)}</span>'
        f'<div><div class="source-title">{title_html}</div>'
        f'<div class="source-snippet">{html.escape(snippet)}</div></div></div>'
    )
