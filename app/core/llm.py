import os
from dotenv import load_dotenv

load_dotenv()

class MistralLLM:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY manquante dans .env")

        # SDK Mistral récent
        from mistralai import Mistral
        self.client = Mistral(api_key=self.api_key)
        self.model = "mistral-small-latest"

    def generate_response(self, prompt: str) -> str:
        response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=220,
        )
        return response.choices[0].message.content.strip()
        


llm = MistralLLM()

