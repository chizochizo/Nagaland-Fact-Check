import os
import json
import re
import datetime
from google import genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class FactChecker:
    def __init__(self):
        # Initialize Groq as the backup engine
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        print("🧠 Logic Engine Initialized: Aggressive 7-Pillar V3 + NEI.")

    def generate_verdict(self, claim, evidence_list, api_key=None):

        # --- 1. SETUP ---
        API_KEY = api_key or os.getenv(
            "GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not API_KEY:
            return {"verdict": "ERROR", "reasoning": "Missing API Key", "confidence": 0}

        # Dynamic Date Handling
        now = datetime.date.today()
        current_month_name = now.strftime("%B")
        current_year_str = str(now.year)
        full_date_str = now.strftime("%B %d, %Y")

        # --- 2. CONTEXT PREPARATION ---
        context_parts = []
        for item in evidence_list:
            context_parts.append(f"[Evidence Source] {str(item)}")

        raw_context = "\n\n".join(
            context_parts) if context_parts else "NO EVIDENCE PROVIDED."

        # Truncate context
        if len(raw_context) > 12000:
            raw_context = raw_context[:12000] + "\n\n[CONTEXT TRUNCATED...]"

        # --- 3. PROMPT (UNCHANGED AS REQUESTED) ---
        prompt = f"""
        ACT AS A SENIOR RESEARCHER AT NAGALAND UNIVERSITY.
        PURPOSE: ELIMINATE AMBIGUITY. PROVIDE A DEFINITIVE VERDICT BASED ON 7-PILLAR VALIDATION.
        SYSTEM TIME: {full_date_str}
        CLAIM: {claim}
        CONTEXT: {raw_context}

        STRICT 7-PILLAR VALIDATION RULES:
        Verify these components against the context:
        1. SUBJECT: The Actor.
        2. ACTION: The Verb/Event.
        3. OBJECT: The Target/Recipient of the action.
        4. LOCATION: Specific Geography.
        5. TIME: MUST match {full_date_str}.
        6. QUANTIFIER: Numbers, amounts, or counts.
        7. QUALIFIER: Scope (e.g., "First time", "Only", "Emergency").

        VERDICT DEFINITIONS:
        - SUPPORTED: Every single pillar matches evidence for {full_date_str}.
        - RECYCLED: Subject/Action/Location match, but TIME is in the past (not {current_month_name} {current_year_str}).
        - REFUTED: 
          a) Direct Contradiction found.
          b) WEAKEST LINK RULE: If any pillar (Object, Quantifier, or Qualifier) is wrong, unverified, or missing, the WHOLE claim is REFUTED.
          c) ABSENCE RULE: If a high-profile public event is not in the context, assume it is FALSE.

        OUTPUT VALID JSON ONLY:
        {{
            "verdict": "SUPPORTED | REFUTED | RECYCLED",
            "confidence": 0-100,
            "pillar_analysis": {{
                "subject": "match/mismatch",
                "action": "match/mismatch",
                "object": "match/mismatch",
                "location": "match/mismatch",
                "time": "match/mismatch",
                "quantifier": "match/mismatch",
                "qualifier": "match/mismatch"
            }},
            "reasoning": "string",
            "evidence_summary": "string"
        }}
        """

        raw_ai_response = ""

        # --- 4. MODEL EXECUTION ---
        try:
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            raw_ai_response = response.text
        except Exception:
            try:
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                raw_ai_response = completion.choices[0].message.content
            except:
                return {"verdict": "ERROR", "reasoning": "Engines Offline.", "confidence": 0}

        # --- 5. PARSING ---
        try:
            clean_ai_response = re.sub(
                r"[\x00-\x1F\x7F]", " ", raw_ai_response)
            json_match = re.search(r'(\{.*\})', clean_ai_response, re.DOTALL)
            data = json.loads(json_match.group(1).strip())

            v = str(data.get("verdict", "")).upper()
            reason = str(data.get("reasoning", "")).lower()
            summary = str(data.get("evidence_summary", "")).lower()

            # =========================
            # 🔥 HARD LOGIC OVERRIDES
            # =========================

            # --- A. WEAKEST LINK RULE ---
            refute_triggers = [
                "partially", "half", "incorrect", "mismatch",
                "unverified", "no mention", "missing info", "not mentioned"
            ]
            if v == "SUPPORTED" and any(t in reason or t in summary for t in refute_triggers):
                data["verdict"] = "REFUTED"
                data["confidence"] = 40
                data["reasoning"] = "Aggressive Override: Partial or unverified claim → REFUTED."

            # --- B. TEMPORAL FIREWALL ---
            months = [
                "january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december"
            ]
            curr_m = current_month_name.lower()

            if v == "SUPPORTED":
                past_month = any(m in summary and m != curr_m for m in months)

                # 🔥 FULL RANGE: 1947 → last year
                years_range = [str(y)
                               for y in range(1947, int(current_year_str))]
                past_year = any(y in summary for y in years_range)

                if past_month or past_year:
                    data["verdict"] = "RECYCLED"
                    data["confidence"] = 95
                    data["reasoning"] = "Temporal Override: Old event reused → RECYCLED."

            # --- C. NOT ENOUGH INFO (NEI) ---
            weak_evidence = [
                "no clear evidence",
                "cannot verify",
                "not enough information",
                "unclear",
                "no data"
            ]

            # Condition 1: No evidence at all
            if "NO EVIDENCE PROVIDED" in raw_context or len(evidence_list) == 0:
                data["verdict"] = "NOT ENOUGH INFO"
                data["confidence"] = 0
                data["reasoning"] = "NEI: No evidence available."

            # Condition 2: Weak / vague reasoning
            elif any(w in reason or w in summary for w in weak_evidence):
                data["verdict"] = "NOT ENOUGH INFO"
                data["confidence"] = 30
                data["reasoning"] = "NEI: Evidence is weak or inconclusive."

            # Condition 3: Too little evidence
            elif len(evidence_list) <= 2 and v != "REFUTED":
                data["verdict"] = "NOT ENOUGH INFO"
                data["confidence"] = 35
                data["reasoning"] = "NEI: Insufficient supporting evidence."

            # --- D. FINAL NORMALIZATION ---
            final_v = str(data.get("verdict", "")).upper()

            if "RECYCLED" in final_v:
                data["verdict"] = "RECYCLED"
            elif "SUPPORT" in final_v:
                data["verdict"] = "SUPPORTED"
            elif "NOT" in final_v:
                data["verdict"] = "NOT ENOUGH INFO"
            else:
                data["verdict"] = "REFUTED"

            return data

        except Exception as e:
            return {
                "verdict": "ERROR",
                "reasoning": f"Parsing Failed: {str(e)}",
                "confidence": 0
            }
