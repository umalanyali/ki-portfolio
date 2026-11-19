import streamlit as st
from dotenv import load_dotenv

from utils.ui import apply_theme, social_links

load_dotenv()

st.set_page_config(page_title="KI-Portfolio", page_icon=":material/auto_awesome:", layout="wide")
apply_theme()
social_links()

navigation = st.navigation(
    {
        "Übersicht": [
            st.Page("pages/0_Start.py", title="Start", icon=":material/home:", default=True),
        ],
        "KI-Agenten": [
            st.Page(
                "pages/1_Dokument_Assistent.py",
                title="Dokument-Assistent",
                icon=":material/description:",
                url_path="dokument-assistent",
            ),
            st.Page(
                "pages/2_Unternehmensanalyse.py",
                title="Unternehmensanalyse",
                icon=":material/domain:",
                url_path="unternehmensanalyse",
            ),
            st.Page(
                "pages/3_KI_Readiness_Check.py",
                title="KI-Readiness-Check",
                icon=":material/speed:",
                url_path="ki-readiness-check",
            ),
        ],
    }
)
navigation.run()
