import streamlit as st
from core.pipeline import answer_query
from fpdf import FPDF
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nagaland Fact-Check System",
                   page_icon="⚖️", layout="wide")

# --- PDF SANITIZATION & GENERATION (THE FIX) ---


def sanitize_text(text):
    """Cleans Unicode characters to prevent PDF export crashes."""
    if not text:
        return ""
    return text.replace('–', '-').replace('—', '-').replace('ü', 'u').encode('latin-1', 'ignore').decode('latin-1')


def generate_pdf(claim, result_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt="NAGALAND UNIVERSITY FACT-CHECK REPORT",
             ln=True, align='C')
    pdf.set_font("Helvetica", size=10)
    pdf.cell(
        200, 10, txt=f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.ln(10)

    sections = [
        ("CLAIM:", claim),
        (f"VERDICT: {result_data['verdict']}",
         f"Confidence: {result_data['confidence']}%"),
        ("REASONING:", result_data['reasoning']),
        ("EVIDENCE SUMMARY:", result_data['evidence_summary'])
    ]

    for title, content in sections:
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(200, 10, txt=sanitize_text(title), ln=True)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 8, txt=sanitize_text(content))
        pdf.ln(5)
    return pdf.output()


# --- HISTORY ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- UI STYLING ---
st.markdown(
    """<style>.evidence-box {background-color: #f8f9fa; padding: 25px; border-radius: 15px; border-left: 10px solid #2c3e50; color: #333 !important; font-size: 1.1rem;}</style>""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("📂 Knowledge Base")
    st.file_uploader("Upload Regional Documents", type=["pdf", "txt"])
    st.markdown("---")
    st.title("📜 Search History")
    for item in reversed(st.session_state.history):
        st.info(f"**Claim:** {item['claim']}\n**Verdict:** {item['verdict']}")

# --- MAIN UI ---
st.title("⚖️ Regional Fact-Checking System")
st.markdown("##### Hybrid RAG Knowledge Verification for Nagaland")

claim = st.text_input("Enter a claim to verify:",
                      placeholder="e.g., Nagaland became a state on Dec 1, 1963.")

if st.button("Verify Claim"):
    if claim:
        with st.spinner("🔍 Consulting regional evidence..."):
            result = answer_query(claim)

        if result["status"] == "success":
            v_data = result["verdict"]
            st.session_state.history.append(
                {"claim": claim, "verdict": v_data["verdict"]})

            st.markdown("---")
            v_col, c_col = st.columns([2, 1])
            with v_col:
                st.subheader("⚖️ Verification Verdict")
                if v_data["verdict"] == "SUPPORTED":
                    st.success(f"### {v_data['verdict']}")
                elif v_data["verdict"] in ["REFUTED", "DISPUTED"]:
                    st.error(f"### {v_data['verdict']}")
                else:
                    st.warning(f"### {v_data['verdict']}")

            with c_col:
                st.metric("System Confidence", f"{v_data['confidence']}%", help=v_data.get(
                    "confidence_reasoning"))
                st.progress(min(v_data['confidence'] / 100.0, 1.0))

            st.info(f"**Reasoning:** {v_data.get('reasoning', 'N/A')}")

            if v_data.get("evidence_summary"):
                st.subheader("📂 Supporting Evidence")
                st.markdown(
                    f'<div class="evidence-box">{v_data["evidence_summary"]}</div>', unsafe_allow_html=True)

            # --- PDF DOWNLOAD ---
            try:
                pdf_bytes = generate_pdf(claim, v_data)
                st.download_button(label="📥 Download PDF Report", data=bytes(
                    pdf_bytes), file_name=f"Report_{datetime.date.today()}.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"PDF Error: {e}")
    else:
        st.warning("Please enter a claim first.")

st.markdown("<br><br>---")
st.caption("🛡️ Final Year Project | Dept. of CSE, Nagaland University")
