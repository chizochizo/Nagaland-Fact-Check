from google import genai  # 👈 Using the new 2026 library
import json


class FactChecker:
    def __init__(self):
        print("🧠 Logic Engine Initialized with Gemini 2.5 (Stable).")

    def generate_verdict(self, claim, evidence_list, api_key=None):
        if not api_key:
            return {"verdict": "ERROR", "explanation": "API Key missing."}

        try:
            # 1. Initialize the new Client
            client = genai.Client(api_key=api_key)

            # 2. Build Context
            context = "\n\n".join(
                [f"Source {i+1}: {text}" for i, (text, score) in enumerate(evidence_list)])

            # 3. Create the prompt
            prompt = f"""
            Compare the CLAIM to the provided EVIDENCE.
            CLAIM: {claim}
            EVIDENCE: {context}
            
            Return ONLY a JSON object:
            {{
                "verdict": "SUPPORTED or REFUTED or NOT ENOUGH EVIDENCE",
                "explanation": "One-sentence reason."
            }}
            """

            # 4. Request using the stable 2.5 model from your list
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )

            # Clean up JSON formatting
            cleaned_text = response.text.replace(
                '```json', '').replace('```', '').strip()
            return json.loads(cleaned_text)

        except Exception as e:
            return {"verdict": "CONNECTION_ERROR", "explanation": str(e)}
