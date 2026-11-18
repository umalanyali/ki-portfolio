import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="KI-Portfolio", page_icon="🤖", layout="wide")

st.title("🤖 KI-Portfolio")
st.write("Willkommen! Wähle links in der Seitenleiste einen der drei KI-Agenten aus.")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("📄 Dokument-Assistent")
    st.write("Fragen an eigene Dokumente stellen.")
with col2:
    st.subheader("🏢 Unternehmensanalyse")
    st.write("Unternehmen strukturiert analysieren.")
with col3:
    st.subheader("✅ KI-Readiness-Check")
    st.write("KI-Reifegrad eines Unternehmens bewerten.")
