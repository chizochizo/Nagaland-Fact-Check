import streamlit as st
from core.pipeline import answer_query

# --- PAGE CONFIG ---
st.set_page_config(page_title="Nagaland Fact-Check System",
                   page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .evidence-box {
        background-color: #f8f9fa; /* 👈 Professional Light Ivory/Grey */
        padding: 30px;
        border-radius: 15px;
        border-left: 12px solid #2c3e50; /* Darker accent for contrast */
        color: #212529 !important;
        font-size: 1.15rem;
        line-height: 1.7;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); /* Subtle shadow for depth */
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Regional Fact-Checking System")
st.markdown("##### Hybrid RAG Knowledge Verification for Nagaland")

claim = st.text_input("Enter a claim to verify:",
                      placeholder="e.g., Mount Saramati is the highest peak in Nagaland.")

if st.button("Verify Claim"):
    if claim:
        with st.spinner("🔍 Deep-scanning regional records..."):
            result = answer_query(claim)

        if result["status"] == "success":
            v_data = result["verdict"]
            conf_score = v_data.get("confidence", 0)

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
                st.metric("System Confidence", f"{conf_score}%")
                st.progress(min(conf_score / 100.0, 1.0))

            st.info(f"**Reasoning:** {v_data.get('reasoning', 'N/A')}")

            if v_data.get("evidence_summary"):
                st.subheader("📂 Supporting Evidence")
                st.markdown(
                    f'<div class="evidence-box">{v_data["evidence_summary"]}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            source_label = result.get(
                "source", "Unknown").replace('_', ' ').title()
            st.caption(
                f"📊 **Data Source:** {source_label} | Nagaland University Research")
    else:
        st.warning("Please enter a claim first.")
