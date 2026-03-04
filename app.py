import streamlit as st
from core.pipeline import answer_query

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Nagaland Fact-Check",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional "Academic Project" look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #0d6efd; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #0b5ed7; border: none; }
    .evidence-box { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .source-badge { padding: 8px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85em; display: inline-block; margin-bottom: 10px; }
    .local-badge { background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc; }
    .live-badge { background-color: #fff3cd; color: #664d03; border: 1px solid #ffecb5; }
    .verdict-header { font-size: 1.8em; font-weight: 800; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🛡️ Nagaland Fake News Detection System")
st.markdown("#### *Hybrid Retrieval-Augmented Generation (RAG) Architecture*")
st.markdown("---")

# --- SIDEBAR: SYSTEM SETTINGS ---
with st.sidebar:
    st.header("🔑 API Authentication")
    api_key = st.text_input("Enter Gemini API Key", type="password",
                            help="Enter your Google AI Studio API key to enable the Reasoning Engine.")

    st.markdown("---")
    st.header("⚙️ System Status")
    st.success("✅ BM25 Sparse Index: Active")
    st.success("✅ FAISS Dense Index: Active")
    st.info("🧠 **Model:** Gemini 2.5 Flash")

    st.markdown("---")
    st.write("**Project Info**")
    st.caption("Final Year Academic Project")
    st.caption("Nagaland University | CS & Engineering")

# --- MAIN INTERFACE ---
claim = st.text_input("Enter a claim to verify about Nagaland:",
                      placeholder="e.g., The Hornbill Festival is held in Kohima.",
                      help="Type a factual statement you want to verify.")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    verify_clicked = st.button("Verify Claim")

if verify_clicked:
    if not api_key:
        st.error(
            "❌ **Authentication Error:** Please provide your Gemini API Key in the sidebar to proceed.")
    elif not claim:
        st.warning("⚠️ **Input Required:** Please enter a claim to verify.")
    else:
        with st.spinner("🔄 Initializing Hybrid Retrieval and AI Reasoning..."):
            # Execute the RAG Pipeline
            result = answer_query(claim, api_key=api_key)

        if result["status"] == "success":
            # ⚖️ VERDICT SECTION
            st.subheader("⚖️ Verification Verdict")
            v_data = result["verdict"]
            verdict_val = v_data.get("verdict", "UNKNOWN")

            if verdict_val == "SUPPORTED":
                st.markdown(
                    f'<div class="verdict-header" style="color: #198754;">✅ {verdict_val}</div>', unsafe_allow_html=True)
                st.balloons()
            elif verdict_val == "REFUTED":
                st.markdown(
                    f'<div class="verdict-header" style="color: #dc3545;">❌ {verdict_val}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="verdict-header" style="color: #ffc107;">⚠️ {verdict_val}</div>', unsafe_allow_html=True)

            st.info(
                f"**Reasoning:** {v_data.get('explanation', 'No explanation provided.')}")

            # 📂 EVIDENCE SECTION
            st.markdown("---")
            st.subheader("📂 Supporting Evidence Content")

            # Show the source of the information
            if result["source"] == "local_hybrid":
                st.markdown(
                    '<span class="source-badge local-badge">📊 DATA SOURCE: LOCAL KNOWLEDGE BASE</span>', unsafe_allow_html=True)
                st.caption(
                    "Verified using pre-indexed local datasets (BM25 + Dense Semantic Search).")
            elif result["source"] == "live_wikipedia":
                st.markdown(
                    '<span class="source-badge live-badge">🌐 DATA SOURCE: LIVE WIKIPEDIA</span>', unsafe_allow_html=True)
                st.caption(
                    "Local data was insufficient; system performed a real-time Wikipedia crawl.")

            # Display the content snippets
            for i, (text, score) in enumerate(result["evidence"]):
                with st.expander(f"📄 View Evidence Snippet {i+1} (Relevance Score: {score:.4f})", expanded=True):
                    st.write(f"\"{text}\"")

        elif result["status"] == "not_found":
            st.error("🕵️ **No Evidence Found:** The system could not find any relevant information in local or live sources to verify this claim.")
        else:
            st.error(
                "🚨 **System Error:** Something went wrong during the verification process.")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2026 Nagaland University | Developed for Academic Submission")
