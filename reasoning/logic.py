from google import genai
import json


class FactChecker:
    def __init__(self):
        print("🧠 Logic Engine Initialized: Detailed Evidence Mode.")

    def generate_verdict(self, claim, evidence_list, api_key=None):
        if not api_key:
            return {"verdict": "ERROR", "reasoning": "API Key missing.", "confidence": 0}

        try:
            client = genai.Client(api_key=api_key)
            raw_context = " ".join([item[1] if isinstance(
                item[0], (int, float)) else item[0] for item in evidence_list])

            prompt = f"""
            ACT AS A SENIOR ACADEMIC RESEARCHER.
            
            CLAIM: {claim}
            CONTEXT: {raw_context}

            INSTRUCTIONS:
            1. VERDICT: Choose SUPPORTED, REFUTED, or DISPUTED.
            2. REASONING: One clear sentence starting with 'Sources explicitly state that...'.
            3. EVIDENCE SUMMARY: Provide a detailed, cohesive paragraph of 7-9 sentences. 
               Include specific dates, locations, and names mentioned in the context.
            4. CONFIDENCE: A whole number (0-100).

            RETURN ONLY JSON:
            {{
                "verdict": "string",
                "confidence": number,
                "reasoning": "string",
                "evidence_summary": "string"
            }}
            """

            response = client.models.generate_content(
                model='gemini-2.5-flash', contents=prompt)
            cleaned_text = response.text.replace(
                '```json', '').replace('```', '').strip()
            data = json.loads(cleaned_text)

            return {
                "verdict": str(data.get("verdict", "NOT ENOUGH EVIDENCE")),
                "confidence": int(data.get("confidence", 0)),
                "reasoning": str(data.get("reasoning", "Sources explicitly state that the evidence is inconclusive.")),
                "evidence_summary": str(data.get("evidence_summary", "No summary available."))
            }
        except Exception as e:
            return {"verdict": "ERROR", "reasoning": str(e), "confidence": 0}
