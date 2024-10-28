from openai import OpenAI

class ChatGPTClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        OpenAI.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        
    def get_response(self, prompt: str, max_tokens: int = 100, temperature: float = 0.5):
        try:
            response = self.client.chat.completions.create (
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
            )

            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error calling ChatGPT API: {e}")
            return None
