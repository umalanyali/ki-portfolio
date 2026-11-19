"""Gemeinsames Design-System der App (Apple-inspiriert, hell und minimalistisch).

Basisfarben für native Widgets kommen aus .streamlit/config.toml; dieses Modul ergänzt
Typografie, Layout, Karten, Chat-Bubbles und Fokuszustände. Icons sind Lucide-SVGs.
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
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>'
    '<path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
}
# Gefüllte Markenlogos (Simple Icons, 24x24)
_BRAND_PATHS = {
    "github": '<path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 '
    "0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744"
    ".084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305"
    ".76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 "
    "1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23"
    ".645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 "
    "2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12\"/>",
    "linkedin": '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 '
    "2.939v5.667H9.351V9h3.414v1.561h.046c.477-.948 1.637-1.84 3.37-1.84 3.601 0 4.267 2.37 4.267 4.874v5.857z"
    "M5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 "
    "1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542"
    "C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z\"/>",
}
_ICON_SIZES = (14, 16, 20, 28, 32)

SOCIAL_LINKS = [
    ("GitHub", "https://github.com/umalanyali", "github"),
    ("LinkedIn", "https://www.linkedin.com/in/ualanyal/", "linkedin"),
]


def icon(name: str, size: int = 28) -> str:
    """Dekoratives Icon. Streamlit entfernt Inline-<svg>, daher als CSS-Maske (färbt sich per currentColor)."""
    if (name not in _ICON_PATHS and name not in _BRAND_PATHS) or size not in _ICON_SIZES:
        raise ValueError(f"Unbekanntes Icon/Größe: {name}/{size}")
    return f'<span class="ui-icon ui-icon-{size} i-{name}" aria-hidden="true"></span>'


def _icon_css() -> str:
    rules = [
        ".ui-icon { display: inline-block; flex: none; vertical-align: -0.15em; background-color: currentColor;"
        " -webkit-mask: var(--icon) center / contain no-repeat; mask: var(--icon) center / contain no-repeat; }"
    ]
    rules += [f".ui-icon-{s} {{ width: {s}px; height: {s}px; }}" for s in _ICON_SIZES]
    for name, paths in _ICON_PATHS.items():
        stroke = 2.5 if name == "chevron-right" else 1.5
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{paths}</svg>'
        )
        rules.append(f'.i-{name} {{ --icon: url("data:image/svg+xml,{quote(svg)}"); }}')
    for name, paths in _BRAND_PATHS.items():
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black">{paths}</svg>'
        rules.append(f'.i-{name} {{ --icon: url("data:image/svg+xml,{quote(svg)}"); }}')
    return "\n".join(rules)


_CSS = """
<style>
:root {
  --bg: #FFFFFF;
  --bg-alt: #F5F5F7;
  --text: #1D1D1F;
  --text-2: #6E6E73;
  --accent: #0071E3;
  --accent-hover: #0077ED;
  --border: #D2D2D7;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-hover: 0 4px 16px rgba(0, 0, 0, 0.08);
  --font: -apple-system, "SF Pro Display", "SF Pro Text", BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
}

/* ---------- Grundlagen ---------- */
.stApp { background: var(--bg); }
.stApp *:not([translate="no"]):not([data-testid="stIconMaterial"]):not(code):not(pre):not(pre *) { font-family: var(--font); }
.stApp { -webkit-font-smoothing: antialiased; color: var(--text); }
:where([data-testid="stMain"]) :where(p, li) { font-size: 17px; line-height: 1.6; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] { max-width: 960px; padding: 1rem 24px 96px; }
[data-testid="stMainBlockContainer"]:has(.st-key-page-header) { padding-top: 0; }
[data-testid="stBottomBlockContainer"] { max-width: 960px; padding-left: 24px; padding-right: 24px; }
/* Unsichtbare Elemente (dieses CSS, Social-Icons) aus dem Fluss nehmen – sonst erzeugen sie je 16px Abstand oben */
[data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] style),
[data-testid="stElementContainer"]:has(.social-corner) { position: absolute; }
[data-testid="stMainBlockContainer"]:has([class*="st-key-action-bar"]) { padding-bottom: 0 !important; }
[data-testid="stAppDeployButton"], footer { display: none; }

/* ---------- Sticky Kopf & Aktionsleiste ----------
   Sticky (nicht fixed): bleibt in der Inhaltsspalte und überdeckt die Sidebar nicht.
   Streamlit legt um Container mit key einen stLayoutWrapper, der nur so hoch ist wie der
   Container – deshalb muss der Wrapper sticky sein, nicht der Container selbst. */
[data-testid="stLayoutWrapper"]:has(> .st-key-page-header) { position: sticky; top: 0; z-index: 100; }
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-action-bar"]) { position: sticky; bottom: 0; z-index: 100; margin-top: auto; }
/* Bei kurzem Inhalt die Spalte auf Fensterhöhe strecken, damit die Leiste trotzdem unten sitzt */
[data-testid="stMainBlockContainer"]:has([class*="st-key-action-bar"]) { min-height: 100dvh; display: flex; flex-direction: column; }
[data-testid="stMainBlockContainer"]:has([class*="st-key-action-bar"]) > [data-testid="stVerticalBlock"] { flex: 1; }
.st-key-page-header, [class*="st-key-action-bar"] {
  background: var(--bg);
  box-shadow: -8px 0 0 var(--bg), 8px 0 0 var(--bg); /* deckt Kartenschatten ab, die seitlich hervorlugen */
}
.st-key-page-header { padding: 16px 0 16px; gap: 12px; border-bottom: 1px solid var(--border); }
[class*="st-key-action-bar"] { border-top: 1px solid var(--border); padding: 16px 0; }
/* Reveal-Leiste: gleitet beim Einfügen von unten herein (Keyframes statt Transition,
   weil Streamlit das Element neu einfügt – eine Transition hätte keinen Ausgangszustand) */
.st-key-action-bar-reveal { animation: bar-reveal 0.4s cubic-bezier(0.16, 1, 0.3, 1) both; }
@keyframes bar-reveal { from { transform: translateY(100%); } to { transform: translateY(0); } }
@media (max-width: 640px), (max-height: 600px) {
  /* Auf kleinen Bildschirmen würde ein fixierter Kopf zu viel Platz belegen */
  [data-testid="stLayoutWrapper"]:has(> .st-key-page-header) { position: static; }
}
a { color: var(--accent); }

.label {
  display: block; font-size: 13px; font-weight: 500; letter-spacing: 0.02em;
  text-transform: uppercase; color: var(--text-2); margin: 0 0 8px;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: var(--bg); }
[data-testid="stSidebarNav"] a { border-radius: 8px; transition: background-color .15s ease; }
[data-testid="stSidebarNav"] a:hover { background: var(--bg-alt); }
[data-testid="stSidebarNav"] a[aria-current="page"] { background: var(--bg-alt); }
[data-testid="stSidebarNav"] a[aria-current="page"] span { color: var(--text); font-weight: 600; }
[data-testid="stNavSectionHeader"], [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
  font-size: 13px !important; font-weight: 500 !important; letter-spacing: 0.02em;
  text-transform: uppercase; color: var(--text-2) !important;
}

/* ---------- Seitenkopf ---------- */
.page-header { padding: 0; margin: 0; }
.page-header h1 {
  font-size: 40px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1;
  color: var(--text); margin: 0; padding: 0;
}
.page-header p { font-size: 17px; line-height: 1.6; color: var(--text-2); margin: 12px 0 0; max-width: 640px; }

.home-hero { text-align: center; padding: 24px 0 48px; }
.home-hero h1 {
  font-size: 56px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.07;
  color: var(--text); margin: 0; padding: 0;
}
.home-hero p { font-size: 21px; line-height: 1.5; color: var(--text-2); margin: 16px auto 0; max-width: 600px; }
@media (max-width: 640px) {
  .home-hero h1 { font-size: 40px; }
  .page-header h1 { font-size: 32px; }
}

/* ---------- Karten ---------- */
.card { background: var(--bg); border-radius: 16px; box-shadow: var(--shadow); padding: 24px; }
.feature-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
@media (max-width: 820px) { .feature-grid { grid-template-columns: 1fr; } }
.feature-card {
  display: flex; flex-direction: column; gap: 12px;
  text-decoration: none !important; color: var(--text) !important;
  transition: box-shadow .2s ease;
}
.feature-card:hover { box-shadow: var(--shadow-hover); }
.feature-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
.feature-card .ui-icon { color: var(--accent); }
.feature-card h3 { font-size: 21px; font-weight: 600; letter-spacing: -0.01em; color: var(--text); margin: 8px 0 0; padding: 0; }
.feature-card p { font-size: 15px; line-height: 1.5; color: var(--text-2); margin: 0; }
.card-link { margin-top: auto; padding-top: 8px; font-size: 15px; color: var(--accent); display: inline-flex; align-items: center; gap: 2px; }
.feature-card:hover .card-link { text-decoration: underline; }
.card-link .ui-icon { transition: transform .2s ease; }
.feature-card:hover .card-link .ui-icon { transform: translateX(2px); }
.stack-note { text-align: center; margin: 48px 0 0; font-size: 13px; color: var(--text-2); }

/* z-index über Streamlits Header (999990), sonst sind die Icons sichtbar, aber nicht klickbar */
.social-corner { position: fixed; top: 20px; right: 24px; z-index: 999991; display: flex; gap: 16px; }
.social-corner a { display: flex; color: #6E6E73 !important; transition: color .15s ease; }
.social-corner a:hover { color: #1D1D1F !important; }

.empty-state { text-align: center; padding: 48px 24px; }
.empty-state .ui-icon { color: var(--text-2); }
.empty-state h3 { font-size: 21px; font-weight: 600; color: var(--text); margin: 16px 0 8px; padding: 0; }
.empty-state p { font-size: 17px; line-height: 1.6; color: var(--text-2); margin: 0 auto; max-width: 440px; }

/* ---------- Buttons ---------- */
.stApp button[kind="primary"], .stApp button[kind="primaryFormSubmit"] {
  background: var(--accent) !important; color: #FFFFFF !important; border: none !important;
  border-radius: 980px !important; font-size: 15px; font-weight: 400; padding: 8px 20px;
  transition: background-color .15s ease;
}
.stApp button[kind="primary"]:hover:not(:disabled), .stApp button[kind="primaryFormSubmit"]:hover:not(:disabled) {
  background: var(--accent-hover) !important;
}
.stApp button[kind="primary"]:disabled, .stApp button[kind="primaryFormSubmit"]:disabled { opacity: .4; }
.stApp button[kind="secondary"], [data-testid="stDownloadButton"] button {
  background: var(--bg-alt) !important; color: var(--text) !important; border: none !important;
  border-radius: 980px !important; transition: background-color .15s ease;
}
.stApp button[kind="secondary"]:hover, [data-testid="stDownloadButton"] button:hover { background: #E8E8ED !important; }
.stApp button:focus-visible, .stApp a:focus-visible { outline: 2px solid var(--accent) !important; outline-offset: 2px; }

/* ---------- Eingaben ---------- */
[data-baseweb="input"], [data-baseweb="textarea"] {
  background: var(--bg) !important; border: 1px solid var(--border) !important; border-radius: 10px !important;
  transition: border-color .15s ease, box-shadow .15s ease;
}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea { background: transparent !important; }
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
  border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15);
}
[data-testid="stForm"] { border: none; padding: 0; background: transparent; }
[data-testid="stFileUploaderDropzone"] {
  background: var(--bg); border: 1px dashed var(--border); border-radius: 12px;
  flex-direction: column; justify-content: center; text-align: center; gap: 8px; padding: 24px 16px;
  transition: border-color .15s ease;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--accent); }
[data-testid="stFileUploaderDropzoneInstructions"] { margin: 0; }

/* ---------- Expander / Status ---------- */
[data-testid="stExpander"] details { background: var(--bg); border: 1px solid var(--border); border-radius: 12px; }
[data-testid="stExpander"] summary:hover { color: var(--accent); }

/* ---------- Chat ---------- */
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none; }
[data-testid="stChatMessage"] {
  width: fit-content; max-width: 80%; padding: 12px 18px; margin-bottom: 12px;
  background: var(--bg); border: 1px solid var(--border); border-radius: 18px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  margin-left: auto; background: var(--bg-alt); border-color: transparent;
}
[data-testid="stChatMessageContent"] { min-width: 0; }
[data-testid="stChatInput"] > div {
  background: var(--bg) !important; border: 1px solid var(--border) !important; border-radius: 22px !important;
  transition: border-color .15s ease, box-shadow .15s ease;
}
[data-testid="stChatInput"] > div:focus-within { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15); }

/* ---------- Quellen ---------- */
.source-card { display: flex; gap: 12px; padding: 12px 14px; margin-bottom: 8px; background: var(--bg-alt); border-radius: 12px; }
.source-card .source-icon { color: var(--text-2); margin-top: 3px; }
.source-card .source-title { font-size: 15px; font-weight: 600; margin-bottom: 2px; color: var(--text); }
.source-card .source-title a { color: var(--text) !important; text-decoration: none; }
.source-card .source-title a:hover { color: var(--accent) !important; text-decoration: underline; }
.source-card .source-snippet { font-size: 13px; line-height: 1.5; color: var(--text-2); }

/* ---------- Report ---------- */
.st-key-report { background: var(--bg); border-radius: 16px; box-shadow: var(--shadow); padding: 32px; margin-bottom: 16px; }
.st-key-report h2 {
  font-size: 28px; font-weight: 600; letter-spacing: -0.01em; color: var(--text);
  margin: 40px 0 12px; padding: 0;
}
.st-key-report h2:first-of-type { margin-top: 0; }
.st-key-report table { width: 100%; border-collapse: collapse; font-size: 15px; }
.st-key-report th { background: var(--bg-alt); text-align: left; font-weight: 600; }
.st-key-report th, .st-key-report td { padding: 10px 12px; border: 1px solid var(--border); }

/* ---------- KI-Readiness-Check ---------- */
.st-key-rc-step { background: var(--bg); border-radius: 16px; box-shadow: var(--shadow); padding: 16px 20px; margin: 4px 0 8px; gap: 12px; }
.rc-step-title { font-size: 22px; font-weight: 600; letter-spacing: -0.01em; color: var(--text); margin: 0; padding: 0; }
.st-key-rc-step [data-testid="stWidgetLabel"] p { font-size: 15px; font-weight: 500; }
.st-key-rc-step [data-testid="stRadio"] [role="radiogroup"] label p { font-size: 15px; }
[data-testid="stProgress"] [role="progressbar"] > div > div,
[data-testid="stProgress"] [role="progressbar"] > div > div > div { height: 4px !important; }

.rc-score-row { display: flex; align-items: center; flex-wrap: wrap; gap: 8px 24px; }
.rc-score-value { display: flex; align-items: baseline; gap: 4px; font-size: 72px; font-weight: 700; letter-spacing: -0.03em; line-height: 1; }
.rc-score-max { font-size: 32px; font-weight: 500; color: var(--text-2); letter-spacing: 0; }

/* Score-Zähler 0 → Ziel: registrierte Integer-Property wird animiert, Zahl per CSS-Counter angezeigt.
   Farbe läuft mit: Rot bis 40, dann zu Orange (bis 55), dann zu Grün (bis 70). Dunkle Apple-Töne
   für ausreichenden Kontrast auf Weiß. Die Keyframes (Zielwert) kommen je Score aus der Seite. */
@property --rc-n { syntax: '<integer>'; inherits: false; initial-value: 0; }
.rc-count {
  font-variant-numeric: tabular-nums; counter-reset: rc-score var(--rc-n);
  animation-duration: 1.5s; animation-timing-function: cubic-bezier(0.33, 1, 0.68, 1); animation-fill-mode: both;
  color: color-mix(in srgb,
    color-mix(in srgb, #D70015, #B25000 calc(clamp(0, (var(--rc-n) - 40) / 15, 1) * 100%)),
    #248A3D calc(clamp(0, (var(--rc-n) - 55) / 15, 1) * 100%));
}
.rc-count::after { content: counter(rc-score); }
.rc-after-count { animation: rc-fade-in .4s ease 1.5s both; }
@keyframes rc-fade-in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

/* Lade-Overlay mit ASCII-Roboter: mittig im Fenster über dem (geblurrten) Fragebogen */
.st-key-rc-loading {
  position: fixed; inset: 0; z-index: 1000; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 4px; background: rgba(255, 255, 255, 0.35);
}
.st-key-rc-loading > [data-testid="stElementContainer"] { width: auto !important; }
.st-key-rc-loading [data-testid="stCode"] { width: auto; box-shadow: var(--shadow); border-radius: 16px; }
.st-key-rc-loading pre { margin: 0; padding: 20px 24px !important; font-size: 15px; line-height: 1.35; background: var(--bg) !important; border-radius: 16px; }
.st-key-rc-loading [data-testid="stCaptionContainer"] { text-align: center; }
.rc-status { display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 980px; font-size: 15px; font-weight: 600; }
.rc-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }
.rc-tone-green, .rc-status-green { color: #248A3D; }
.rc-tone-amber, .rc-status-amber { color: #B25000; }
.rc-tone-red, .rc-status-red { color: #D70015; }
.rc-status-green { background: #EAF7EE; }
.rc-status-amber { background: #FFF4E5; }
.rc-status-red { background: #FFF0F0; }
.rc-summary { font-size: 19px; line-height: 1.55; color: var(--text); max-width: 720px; margin: 8px 0 0; }

.rc-section { font-size: 28px; font-weight: 600; letter-spacing: -0.01em; color: var(--text); margin: 48px 0 16px; padding: 0; }
.rc-cats { display: grid; gap: 14px; }
.rc-cat { display: grid; grid-template-columns: 180px 1fr 48px; align-items: center; gap: 16px; font-size: 15px; }
.rc-bar { height: 6px; border-radius: 3px; background: var(--bg-alt); overflow: hidden; }
.rc-bar-fill { height: 100%; background: var(--accent); border-radius: 3px; }
.rc-cat-value { text-align: right; color: var(--text-2); font-variant-numeric: tabular-nums; }
@media (max-width: 640px) { .rc-cat { grid-template-columns: 1fr 48px; } .rc-bar { grid-column: 1 / -1; grid-row: 2; } }

.rc-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
@media (max-width: 820px) { .rc-grid { grid-template-columns: 1fr; } }
.rc-point h3, .rc-rec h3 { font-size: 17px; font-weight: 600; color: var(--text); margin: 0 0 6px; padding: 0; }
.rc-point p, .rc-rec p { font-size: 15px; line-height: 1.5; color: var(--text-2); margin: 0; }
.rc-recs { display: grid; gap: 12px; }
.rc-rec-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
.rc-badge { flex: none; font-size: 12px; font-weight: 600; letter-spacing: 0.02em; text-transform: uppercase; padding: 4px 10px; border-radius: 980px; }
.rc-badge-hoch { color: #D70015; background: #FFF0F0; }
.rc-badge-mittel { color: #B25000; background: #FFF4E5; }
.rc-badge-niedrig { color: var(--text-2); background: var(--bg-alt); }
.rc-time-value { font-size: 28px; font-weight: 700; letter-spacing: -0.01em; color: var(--text); }
.rc-time p { font-size: 15px; line-height: 1.5; color: var(--text-2); margin: 6px 0 0; }
.rc-note { font-size: 13px; color: var(--text-2); margin: 24px 0; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition: none !important; animation: none !important; }
}
</style>
"""


def apply_theme() -> None:
    st.markdown(_CSS.replace("</style>", _icon_css() + "\n</style>"), unsafe_allow_html=True)


def social_links() -> None:
    """GitHub/LinkedIn als reine Icons oben rechts – app.py läuft bei jedem Seitenaufruf, also überall sichtbar."""
    links = "".join(
        f'<a href="{url}" rel="noopener" aria-label="{name}" title="{name}">{icon(key, 20)}</a>'
        for name, url, key in SOCIAL_LINKS
    )
    st.markdown(f'<nav class="social-corner" aria-label="Profile">{links}</nav>', unsafe_allow_html=True)


def page_header(title: str, description: str, label: str = ""):
    """Sticky Seitenkopf. Gibt den Container zurück, damit Seiten z. B. Fortschritt oder Score anhängen können."""
    label_html = f'<span class="label">{html.escape(label)}</span>' if label else ""
    header = st.container(key="page-header")
    header.html(
        f'<header class="page-header">{label_html}<h1>{html.escape(title)}</h1>'
        f"<p>{html.escape(description)}</p></header>"
    )
    return header


def action_bar(reveal: bool = False):
    """Sticky Leiste am unteren Rand für die Hauptaktionen. Muss das letzte Element der Seite sein.

    reveal=True: Leiste gleitet beim Erscheinen von unten herein (z. B. sobald ein Report vorliegt).
    """
    return st.container(key="action-bar-reveal" if reveal else "action-bar")


def empty_state(icon_name: str, title: str, text: str) -> None:
    st.html(
        f'<div class="card empty-state">{icon(icon_name, 32)}'
        f"<h3>{html.escape(title)}</h3><p>{html.escape(text)}</p></div>"
    )


def source_card(title: str, snippet: str, url: str | None = None) -> str:
    """HTML einer Quellenkarte; mit `url` wird der Titel zum externen Link."""
    title_html = html.escape(title)
    if url:
        title_html = f'<a href="{html.escape(url, quote=True)}" rel="noopener">{title_html}</a>'
    return (
        f'<div class="source-card"><span class="source-icon">{icon("link" if url else "file-text", 14)}</span>'
        f'<div><div class="source-title">{title_html}</div>'
        f'<div class="source-snippet">{html.escape(snippet)}</div></div></div>'
    )
