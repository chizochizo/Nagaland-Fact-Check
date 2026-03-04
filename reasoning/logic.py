from google import genai
import json


class FactChecker:
    def __init__(self):
        print("🧠 Logic Engine Initialized: Universal High-Precision Mode.")

    def generate_verdict(self, claim, evidence_list, api_key=None):
        if not api_key:
            return {"verdict": "ERROR", "reasoning": "API Key missing.", "confidence": 0}

        try:
            client = genai.Client(api_key=api_key)
            # Merges all retrieved data into one knowledge block
            raw_context = " ".join([item[1] if isinstance(
                item[0], (int, float)) else item[0] for item in evidence_list])

            prompt = f"""
            ACT AS A SENIOR ACADEMIC RESEARCHER AND FACT-CHECKER.
            
            CLAIM: {claim}
            CONTEXT: {raw_context}

            INSTRUCTIONS:
            1. VERDICT: Choose SUPPORTED, REFUTED, or DISPUTED.
            2. REASONING: One sentence starting with 'Sources explicitly state that...'.
            3. EVIDENCE SUMMARY: Write a cohesive 7-9 sentence paragraph summarizing the core facts. 
               FOCUS on official data and ignore temporary event-specific numbers unless directly asked.
            4. CONFIDENCE: A whole number (0-100). Prioritize administrative/official records over specific event details.
            5. CONFIDENCE REASONING: One SHORT sentence (max 15 words) explaining why this score was given.

            RETURN ONLY JSON:
            {{
                "verdict": "string",
                "confidence": number,
                "reasoning": "string",
                "evidence_summary": "string",
                "confidence_reasoning": "string"
            }}
            """

            response = client.models.generate_content(
                model='gemini-2.5-flash', contents=prompt)
            cleaned_text = response.text.replace(
                '```json', '').replace('```', '').strip()
            data = json.loads(cleaned_text)

            # Safety Guard: Ensures keys exist and types are correct
            return {
                "verdict": str(data.get("verdict", "NOT ENOUGH EVIDENCE")),
                "confidence": int(data.get("confidence", 0)),
                "reasoning": str(data.get("reasoning", "Sources explicitly state that the evidence is inconclusive.")),
                "evidence_summary": str(data.get("evidence_summary", "No detailed summary available.")),
                "confidence_reasoning": str(data.get("confidence_reasoning", "Score determined by contextual source relevance."))
            }
        except Exception as e:
            return {"verdict": "ERROR", "reasoning": str(e), "confidence": 0}
