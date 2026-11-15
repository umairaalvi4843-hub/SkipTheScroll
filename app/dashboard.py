"""One-tab ClauseClear demo. Run: streamlit run app/dashboard.py"""
import streamlit as st
from src.pipeline import run

st.set_page_config(page_title="ClauseClear — Skip the Scroll", layout="wide")
st.title("ClauseClear")
st.caption("Plain-language Terms and Conditions analysis, with verified quotes. English and Hindi.")
st.warning("Information only, not legal advice. Consult a qualified professional for decisions.")

tab_analyse, tab_about = st.tabs(["Analyse", "About"])
with tab_analyse:
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.subheader("Input")
        text = st.text_area("Paste a Terms and Conditions section:", height=350, value="")
        version = st.selectbox("Prompt version", ["v2", "v3", "v4"], index=2)
        run_btn = st.button("Analyse")
    with col_right:
        st.subheader("Output")
        if run_btn and text.strip():
            with st.spinner("Running pipeline..."):
                out = run(text, version)
            st.markdown(f"**Summary:** {out.get('summary', '')}")
            clauses = out.get("clauses", [])
            if not clauses:
                st.info("No risky clauses found in this section.")
            for c in clauses:
                badge = "verified" if c.get("quote_verified") else "unverified"
                st.markdown(f"**{c.get('category', '—')}** | risk: `{c.get('risk_level', '—')}` | {badge}")
                st.markdown(f"> {c.get('quote', '')}")
                st.caption(f"EN: {c.get('explanation_en', '')}")
                st.caption(f"HI: {c.get('explanation_hi', '')}")
                st.divider()
            st.caption(out.get("disclaimer", ""))
        elif run_btn:
            st.info("Paste some text first.")
with tab_about:
    st.markdown("""
    **ClauseClear** compares prompt strategies for explaining Terms and Conditions.
    - v0 baseline to v4 with verifier
    - Verified quotes: every clause's quote must appear verbatim in the source
    - Hindi/Hinglish explanations rated by human readers
    Legal-topic rule: information only, no legal advice.
    """)
