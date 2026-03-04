# 🛡️ Nagaland Fact-Check System: Hybrid RAG Architecture

An AI-powered fact-verification system designed specifically for the regional context of Nagaland. This project utilizes a **Hybrid Retrieval-Augmented Generation (RAG)** pipeline to detect misinformation by comparing user claims against a curated local knowledge base and live web sources.

---

## 🚀 Key Features
* **Hybrid Search:** Combines **Sparse Retrieval (BM25)** for keyword matching and **Dense Retrieval (FAISS)** for semantic meaning.
* **Live Fallback:** Automatically queries the Wikipedia API if the local knowledge base contains insufficient information.
* **Explainable AI:** Uses **Gemini 2.5 Flash** to provide a verdict (SUPPORTED/REFUTED) with a detailed explanation and direct citations from the evidence.
* **Dynamic UI:** A clean, professional Streamlit interface designed for real-time fact-checking.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Frontend:** [Streamlit](https://streamlit.io/)
* **LLM Engine:** Google Gemini 2.5 Flash (via `google-genai` SDK)
* **Vector Store:** FAISS (Facebook AI Similarity Search)
* **Retrieval:** Rank-BM25 & Sentence-Transformers (`all-MiniLM-L6-v2`)

## 📂 Project Structure
```text
.
├── app.py                # Main Streamlit UI
├── core/
│   └── pipeline.py       # Hybrid retrieval & orchestration logic
├── reasoning/
│   └── logic.py          # Gemini 2.5 reasoning & citation extraction
├── data/                 # Raw Nagaland datasets (CSVs/TXTs)
└── index/                # Pre-computed BM25 & Dense indices


🛡️ Disclaimer

This project is an Academic Milestone for the Final Year Project at Nagaland University. The system is designed to demonstrate the efficacy of Hybrid RAG (Retrieval-Augmented Generation) in regional fact-checking and should be used with verified datasets for critical applications.

Developed by: [Vechikho Chizo]Department: Computer Science & Engineering, Nagaland University.
