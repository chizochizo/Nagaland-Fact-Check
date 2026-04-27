import os
import json
import re
import datetime
from google import genai
from google.genai import types
from groq import Groq  # Added Groq import
from dotenv import load_dotenv

load_dotenv()


class FactChecker:
    def __init__(self):
        # Initialize Groq client alongside the existing print statement
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        print("🧠 Logic Engine Initialized: Nagaland University Temporal Suite (2026) with Groq Fallback.")

    def generate_verdict(self, claim, evidence_list, api_key=None):
        # 1. SETUP KEYS & DATE
        API_KEY = api_key or os.getenv(
            "GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not API_KEY:
            return {"verdict": "ERROR", "reasoning": "Missing API Key", "confidence": 0}

        current_date = datetime.date.today().strftime("%B %d, %Y")

        # --- CONTEXT CLEANER (Kept exactly as yours) ---
        context_parts = []
        for item in evidence_list:
            if isinstance(item, tuple):
                context_parts.append(f"[Score: {item[0]}] {str(item[1])}")
            else:
                context_parts.append(str(item))

        raw_context = "\n\n".join(
            context_parts) if context_parts else "NO EVIDENCE FOUND."

        # --- PROMPT (Kept exactly as yours) ---
        prompt = f"""
        ACT AS A SENIOR ACADEMIC RESEARCHER AT NAGALAND UNIVERSITY.
        TODAY'S DATE: {current_date}

        CLAIM: {claim}
        CONTEXT: {raw_context}

        STRICT LOGIC RULES:
        1. TEMPORAL PRIORITIZATION: If the claim is about 'current status' or '2026', you MUST prioritize context tagged with 'NEWS' or 'VIDEO' from 2025/2026.
        2. CONFLICT RESOLUTION: If a 2018 PDF contradicts a 2026 News link, the 2026 News link is the TRUTH.
        3. HALLUCINATION GUARD: If CONTEXT is 'NO EVIDENCE FOUND', you MUST return 'NOT ENOUGH INFO' and 0% confidence.
        4. REASONING: Explain 'Why' based on the dates. (e.g., "While 2018 records show X, 2026 news confirms Y").
        5. EVIDENCE_SUMMARY: 7-8 lines citing specific URLs and dates found in the context.

        OUTPUT ONLY VALID JSON:
        {{
            "verdict": "SUPPORTED | REFUTED | NOT ENOUGH INFO",
            "confidence": 0-100,
            "reasoning": "string",
            "evidence_summary": "string"
        }}
        """

        raw_ai_response = ""

        # --- PLAN A: GEMINI ---
        try:
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            raw_ai_response = response.text

        # --- PLAN B: GROQ FALLBACK ---
        except Exception as gemini_error:
            print(f"⚠️ Gemini failed: {gemini_error}. Switching to Groq...")
            try:
                # Using Llama 3.1 8B for fast, reliable backup
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1  # Low temperature for factual accuracy
                )
                raw_ai_response = completion.choices[0].message.content
            except Exception as groq_error:
                return {
                    "verdict": "ERROR",
                    "reasoning": f"Both engines failed. Gemini Error: {gemini_error} | Groq Error: {groq_error}",
                    "confidence": 0
                }

        # --- SHARED EXTRACTION LOGIC (Your original cleanup) ---
        try:
            json_match = re.search(r'(\{.*\})', raw_ai_response, re.DOTALL)
            data = json.loads(json_match.group(1).strip())

            v = str(data.get("verdict", "")).upper()
            if "SUPPORT" in v:
                data["verdict"] = "SUPPORTED"
            elif "REFUTE" in v or "FALSE" in v:
                data["verdict"] = "REFUTED"
            else:
                data["verdict"] = "NOT ENOUGH INFO"
                data["confidence"] = data.get("confidence", 0)

            return data

        except Exception as parse_error:
            return {
                "verdict": "ERROR",
                "reasoning": f"Parsing Failure: {str(parse_error)}",
                "evidence_summary": "Technical error in processing AI response.",
                "confidence": 0
            }
