import io
import os
import uuid

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from utils.ui import empty_state, page_header, source_card

load_dotenv()

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Du bist ein hilfreicher Dokument-Assistent. Beantworte die Frage ausschließlich "
            "auf Basis des folgenden Kontexts aus den hochgeladenen Dokumenten. "
            "Wenn die Antwort nicht im Kontext steht, sage ehrlich, dass du es in den "
            "Dokumenten nicht finden konntest. Antworte auf Deutsch, klar und präzise. "
            "Verweise im Text auf die Quellen im Format (Dokument, S. X).\n\n"
            "Kontext:\n{context}",
        ),
        ("human", "{question}"),
    ]
)


def build_vectorstore(uploaded_files) -> tuple[Chroma, list[str]]:
    """Lädt die PDFs, zerlegt sie in Chunks und legt sie in einer neuen Chroma-Collection ab."""
    documents = []
    empty_files = []
    for uploaded in uploaded_files:
        reader = PdfReader(io.BytesIO(uploaded.getvalue()))
        pages = [
            Document(page_content=text, metadata={"source": uploaded.name, "page": number})
            for number, page in enumerate(reader.pages, start=1)
            if (text := page.extract_text() or "").strip()
        ]
        if not pages:
            empty_files.append(uploaded.name)
            continue
        documents.extend(pages)

    if not documents:
        raise ValueError("In den hochgeladenen PDFs wurde kein auslesbarer Text gefunden.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        chunks,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        collection_name=f"docs-{uuid.uuid4().hex}",
    )
    return vectorstore, empty_files


def format_context(docs) -> str:
    return "\n\n---\n\n".join(
        f"[Dokument: {d.metadata['source']}, Seite {d.metadata['page']}]\n{d.page_content}"
        for d in docs
    )


def unique_sources(docs) -> list[dict]:
    """Fasst Treffer pro (Dokument, Seite) zusammen, Reihenfolge nach Relevanz."""
    seen = {}
    for d in docs:
        key = (d.metadata["source"], d.metadata["page"])
        if key not in seen:
            snippet = " ".join(d.page_content.split())
            seen[key] = {
                "source": key[0],
                "page": key[1],
                "snippet": snippet[:220] + ("…" if len(snippet) > 220 else ""),
            }
    return list(seen.values())


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"Quellen ({len(sources)})", icon=":material/menu_book:"):
        st.html("".join(source_card(f"{s['source']} · Seite {s['page']}", s["snippet"]) for s in sources))


def reset_index() -> None:
    if st.session_state.get("vectorstore") is not None:
        st.session_state.vectorstore.delete_collection()
    st.session_state.vectorstore = None
    st.session_state.indexed_files = []
    st.session_state.messages = []


# --- Session State ---
st.session_state.setdefault("vectorstore", None)
st.session_state.setdefault("indexed_files", [])
st.session_state.setdefault("messages", [])

# --- Header ---
page_header(
    "Dokument-Assistent",
    "Lade PDFs hoch und stelle Fragen dazu. Jede Antwort enthält die Quellen mit Dokument und Seitenzahl.",
    label="Agent 01",
)

if not os.getenv("OPENAI_API_KEY"):
    st.error("Kein OpenAI API-Key gefunden. Bitte `OPENAI_API_KEY` in der `.env`-Datei eintragen und die App neu starten.")
    st.stop()

# --- Sidebar: Upload & Verarbeitung ---
with st.sidebar:
    st.header("Dokumente")
    uploaded_files = st.file_uploader(
        "PDF-Dateien hochladen",
        type="pdf",
        accept_multiple_files=True,
        help="Du kannst ein oder mehrere PDFs gleichzeitig hochladen.",
    )

    if st.button("Dokumente verarbeiten", type="primary", use_container_width=True, disabled=not uploaded_files):
        reset_index()
        with st.spinner("Dokumente werden gelesen und indexiert …"):
            try:
                vectorstore, empty_files = build_vectorstore(uploaded_files)
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Fehler bei der Verarbeitung: {e}")
            else:
                st.session_state.vectorstore = vectorstore
                st.session_state.indexed_files = [f.name for f in uploaded_files if f.name not in empty_files]
                for name in empty_files:
                    st.warning(f"„{name}“ enthält keinen auslesbaren Text (evtl. gescannt) und wurde übersprungen.")

    if st.session_state.indexed_files:
        st.success(f"{len(st.session_state.indexed_files)} Dokument(e) bereit")
        for name in st.session_state.indexed_files:
            st.markdown(f":material/description: {name}")

    if st.session_state.messages:
        st.divider()
        if st.button("Chat leeren", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# --- Chat ---
if st.session_state.vectorstore is None:
    empty_state(
        "upload",
        "Noch keine Dokumente",
        "Lade links ein oder mehrere PDFs hoch und klicke auf „Dokumente verarbeiten“, um zu starten.",
    )
    st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        render_sources(msg.get("sources", []))

if question := st.chat_input("Stelle eine Frage zu deinen Dokumenten …"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Suche relevante Textstellen …"):
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": TOP_K})
                docs = retriever.invoke(question)

            chain = PROMPT | ChatOpenAI(model="gpt-4o-mini", temperature=0) | StrOutputParser()
            answer = st.write_stream(chain.stream({"context": format_context(docs), "question": question}))
            sources = unique_sources(docs)
            render_sources(sources)
        except Exception as e:
            answer = f"Es ist ein Fehler aufgetreten: {e}"
            sources = []
            st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
