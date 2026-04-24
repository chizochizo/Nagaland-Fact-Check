import streamlit as st
from core.pipeline import answer_query
from fpdf import FPDF
import datetime
import re

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Nagaland Fact-Check System",
    page_icon="⚖️",
    layout="wide"
)

# --- 2. PDF GENERATION HELPER ---


def sanitize_latin(text):
    """Ensures text is compatible with FPDF Latin-1 encoding."""
    if not text:
        return ""
    return str(text).replace('–', '-').replace('—', '-').replace('’', "'").replace('‘', "'").encode('latin-1', 'ignore').decode('latin-1')


def generate_pdf(claim, result_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt="NAGALAND UNIVERSITY FACT-CHECK REPORT",
             ln=True, align='C')
    pdf.ln(10)

    sections = [
        ("CLAIM UNDER REVIEW:", claim),
        (f"OFFICIAL VERDICT: {result_data.get('verdict')}",
         f"Confidence: {result_data.get('confidence', 0)}%"),
        ("EXECUTIVE REASONING:", result_data.get('reasoning')),
        ("DETAILED EVIDENCE SUMMARY:", result_data.get('evidence_summary'))
    ]

    for title, content in sections:
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(200, 10, txt=sanitize_latin(title), ln=True)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 8, txt=sanitize_latin(content))
        pdf.ln(5)

    pdf.set_font("Helvetica", 'I', 8)
    pdf.cell(
        0, 10, txt=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", align='R')
    return pdf.output(dest='S').encode('latin-1')


# --- 3. CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    .evidence-box {
        background-color: #1a2a3a;
        padding: 25px;
        border-radius: 12px;
        border-left: 10px solid #2c3e50;
        color: #ffffff !important;
        font-size: 1.1rem;
        line-height: 1.7;
    }
    .stMetric {
        background-color: #0e1117;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. TOP SECTION: HEADER & INPUT ---
st.title("⚖️ Nagaland Fact-Checking System")
st.caption(
    "🛡️ Final Year Project | Dept. of CSE, Nagaland University | Live RAG Engine 2026")

claim_input = st.text_input("Enter a claim to verify:",
                            placeholder="e.g., Nagaland has 17 districts as of 2026.")

st.divider()

# --- 5. MIDDLE SECTION: UPLOAD & ACTIONS ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📂 Knowledge Base")
    uploaded_file = st.file_uploader(
        "Upload Regional Documents (PDF/TXT)", type=["pdf", "txt"])
    st.info("System scans local PDFs, Google News, and YouTube Metadata.")

with col_right:
    st.subheader("🚀 Action Center")
    if st.button("Verify Claim", use_container_width=True, type="primary"):
        if claim_input:
            with st.spinner("🔍 Analyzing Evidence & Checking Live Sources..."):
                extracted_text = ""
                if uploaded_file:
                    extracted_text = uploaded_file.read().decode("utf-8", errors="ignore")

                # Run Pipeline
                result = answer_query(
                    claim_input, uploaded_text=extracted_text)

                if result["status"] == "success":
                    v_data = result["verdict"]
                    st.session_state.last_result = {
                        "claim": claim_input, "v_data": v_data}

                    if "history" not in st.session_state:
                        st.session_state.history = []
                    st.session_state.history.append(
                        {"claim": claim_input, "verdict": v_data["verdict"]})
                else:
                    st.error(f"❌ Error: {result['message']}")
        else:
            st.warning("⚠️ Please enter a claim first.")

# --- 6. RESULTS SECTION (DYNAMICAL) ---
if "last_result" in st.session_state:
    res = st.session_state.last_result
    v_data = res["v_data"]

    st.markdown("---")
    res_col, met_col = st.columns([3, 1])

    with res_col:
        st.subheader("⚖️ Verdict Analysis")
        v_type = str(v_data.get("verdict", "NOT ENOUGH INFO")).upper()

        if v_type == "SUPPORTED":
            st.success(f"### ✅ {v_type}")
        elif v_type == "REFUTED":
            st.error(f"### ❌ {v_type}")
        else:
            st.warning(f"### ⚠️ {v_type}")
            st.caption(
                "🛡️ Hallucination Guard: No strong evidence found in trusted sources.")

        st.info(f"**Reasoning:** {v_data.get('reasoning')}")

    with met_col:
        st.metric("Confidence Score", f"{v_data.get('confidence', 0)}%")

    # --- 🎥 LIVE VIDEO PLAYER ---
    evidence_text = v_data.get('evidence_summary', '')
    # Use Regex to find the first YouTube URL in the evidence
    yt_links = re.findall(
        r'(https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+)', evidence_text)

    if yt_links:
        st.subheader("📺 Video Evidence Found")
        st.video(yt_links[0])
        st.caption(f"Source: {yt_links[0]}")

    # --- 📂 EVIDENCE BOX ---
    st.subheader("📂 Supporting Evidence Summary")
    st.markdown(
        f'<div class="evidence-box">{evidence_text}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 📥 DOWNLOAD BUTTON ---
    pdf_bytes = generate_pdf(res["claim"], v_data)
    st.download_button(
        label="📥 Download Official Fact-Check Report (PDF)",
        data=pdf_bytes,
        file_name=f"Nagaland_FactCheck_{datetime.date.today()}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# --- 7. SIDEBAR: HISTORY ---
with st.sidebar:
    st.title("📜 History")
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.session_state.last_result = None
        st.rerun()

    st.divider()
    if "history" in st.session_state:
        for item in reversed(st.session_state.history):
            h_v = item['verdict']
            if h_v == "SUPPORTED":
                st.info(f"**{item['claim']}**\n\nVerdict: {h_v}")
            elif h_v == "REFUTED":
                st.error(f"**{item['claim']}**\n\nVerdict: {h_v}")
            else:
                st.warning(f"**{item['claim']}**\n\nVerdict: {h_v}")

st.divider()
