"""ScrollLess - Interactive T&C Explainer"""
import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline import run

st.set_page_config(page_title="ScrollLess", layout="wide", page_icon="🧈")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');

    /* Force Streamlit to stop cutting off content */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
        max-width: 95% !important;
    }
    
    .stApp {
        background-color: #FFF9E6 !important;
        font-family: 'Outfit', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        color: #3D3B40 !important;
    }

    /* The magic fix: One container for everything */
    .header-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 10px;
        margin-bottom: 10px;
    }

    .icon-row {
        display: flex;
        gap: 25px;
        margin-bottom: 5px;
    }

    .big-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 4rem !important;
        font-weight: 700 !important;
        color: #3D3B40 !important;
        text-align: center;
        margin: 0;
        padding: 0;
        line-height: 1.2 !important;
    }
    
    .sub-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        color: #6B6A65;
        text-align: center;
        margin-bottom: 15px;
    }
    
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #3D3B40 !important;
        border: 2px solid #E0D8C8 !important;
        border-radius: 12px !important;
        font-family: 'Courier New', monospace !important;
    }

    .clause-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(160, 140, 100, 0.1);
        border-left: 6px solid #4CAF50;
    }
    .clause-card.high { border-left-color: #FF6B6B; }
    .clause-card.medium { border-left-color: #FFB347; }
    .clause-card.low { border-left-color: #4CAF50; }
    
    .risk-pill {
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 0.7em;
        font-weight: 800;
        text-transform: uppercase;
        color: white;
    }
    .risk-high { background-color: #FF6B6B; }
    .risk-medium { background-color: #FFB347; color: #333;}
    .risk-low { background-color: #4CAF50; }
    
    .quote-box {
        font-family: 'Courier New', Courier, monospace;
        background-color: #F9F9F9;
        padding: 10px;
        border-radius: 8px;
        color: #444;
        margin: 10px 0;
        border-left: 3px solid #E0E0E0;
        font-size: 0.85rem;
    }
    
    .stAlert {
        background-color: #FFF3CD !important;
        color: #856404 !important;
        border: 1px solid #FFEEBA !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    .stButton > button {
        background-color: #FFB347 !important;
        color: #3D3B40 !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Everything in one single HTML block to prevent cutting
st.markdown("""
<div class="header-wrapper">
    <div class="icon-row">
        <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#FFB347" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#FF6B6B" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>
    </div>
    <p class="big-title">ScrollLess</p>
    <p class="sub-title">Stop scrolling. Start understanding. Verified plain-language T&C analysis.</p>
</div>
""", unsafe_allow_html=True)

st.warning("⚠️ **Disclaimer:** Information only, not legal advice. Always consult a qualified professional for legal decisions.")

tab_analyse, tab_about = st.tabs(["🚀 Analyse Document", "ℹ️ About Project"])

with tab_analyse:
    col_left, col_right = st.columns([1, 1.2], gap="large")
    
    with col_left:
        text = st.text_area("Paste your Terms & Conditions:", height=280, placeholder="Paste a long, boring T&C section here...", label_visibility="visible")
        
        col_v, col_b = st.columns([1, 1])
        with col_v:
            version = st.selectbox("Prompt Engine", ["v4 (Best)", "v3 (Chained)", "v2 (JSON)"], index=0)
        with col_b:
            st.write("") 
            st.write("") 
            run_btn = st.button("✨ Analyse Now", use_container_width=True, type="primary")

    with col_right:
        if run_btn and text.strip():
            v_code = version.split(" ")[0] 
            
            with st.spinner("Scanning text and verifying quotes..."):
                out = run(text, v_code)
            
            st.success(f"**TL;DR Summary:**\n\n{out.get('summary', '')}")
            
            clauses = out.get("clauses", [])
            if not clauses:
                st.write("✅ No risky clauses detected in this section.")
            else:
                st.write(f"Found **{len(clauses)}** potentially risky clauses:")
                
                for c in clauses:
                    risk = c.get("risk_level", "low").lower()
                    verified_badge = "✅ Verified" if c.get("quote_verified") else "❌ Unverified"
                    
                    html_card = f"""
                    <div class="clause-card {risk}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <h3 style="margin: 0; color: #3D3B40; font-size: 1.1rem;">{c.get('category', 'Unknown')}</h3>
                            <span class="risk-pill risk-{risk}">{risk} risk</span>
                        </div>
                        <div class="quote-box">"{c.get('quote', '')}"</div>
                        <p style="margin: 5px 0; color: #444; font-size: 0.9rem;"><strong>🇬🇧 EN:</strong> {c.get('explanation_en', '')}</p>
                        <p style="margin: 5px 0; color: #444; font-size: 0.9rem;"><strong>🇮🇳 HI:</strong> {c.get('explanation_hi', '')}</p>
                        <div style="font-size: 0.8em; color: #888; text-align: right; font-weight: 600; margin-top: 5px;">{verified_badge}</div>
                    </div>
                    """
                    st.markdown(html_card, unsafe_allow_html=True)
                    
        elif run_btn:
            st.toast("Please paste some text first!", icon="⚠️")

with tab_about:
    st.markdown("""
    ### About ScrollLess
    **ScrollLess** is a Prompt Engineering mini-project for Bennett University.
    
    We compare prompt strategies (v0 to v4) to see how well Large Language Models can extract and explain unfair clauses from Terms of Service.
    
    *   **v2** adds strict JSON schema and few-shot examples.
    *   **v3** chains extraction, classification, and summarization.
    *   **v4** adds a dual-verification step (LLM + code string matching) to eliminate hallucinated quotes.
    
    *Built with Streamlit and Gemini 3.5 Flash Lite.*
    """)
