import os
import json
import re
import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class FactChecker:
    def __init__(self):
        print("🧠 Logic Engine Initialized: Nagaland University Temporal Suite (2026).")

    def generate_verdict(self, claim, evidence_list, api_key=None):
        API_KEY = api_key or os.getenv(
            "GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not API_KEY:
            return {"verdict": "ERROR", "reasoning": "Missing API Key", "confidence": 0}

        # 1. GET DYNAMIC DATE
        current_date = datetime.date.today().strftime("%B %d, %Y")

        try:
            client = genai.Client(api_key=API_KEY)

            # --- CONTEXT CLEANER ---
            context_parts = []
            for item in evidence_list:
                if isinstance(item, tuple):
                    context_parts.append(f"[Score: {item[0]}] {str(item[1])}")
                else:
                    context_parts.append(str(item))

            raw_context = "\n\n".join(
                context_parts) if context_parts else "NO EVIDENCE FOUND."

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

            response = client.models.generate_content(
                model='gemini-2.0-flash',  # Use the latest available model
                contents=prompt
            )

            # Extract JSON
            json_match = re.search(r'(\{.*\})', response.text, re.DOTALL)
            data = json.loads(json_match.group(1).strip())

            # --- FINAL REFINEMENT & COLOR LOGIC ---
            v = str(data.get("verdict", "")).upper()
            if "SUPPORT" in v:
                data["verdict"] = "SUPPORTED"
            elif "REFUTE" in v or "FALSE" in v:
                data["verdict"] = "REFUTED"
            else:
                data["verdict"] = "NOT ENOUGH INFO"
                data["confidence"] = data.get("confidence", 0)

            return data

        except Exception as e:
            return {
                "verdict": "ERROR",
                "reasoning": f"Logic Failure: {str(e)}",
                "evidence_summary": "Technical error in processing logic.",
                "confidence": 0
            }
