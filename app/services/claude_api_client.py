from anthropic import Anthropic, APIStatusError, APIError
from app.config import ANTHROPIC_API_KEY, MODEL

class ClaudeAPIClient:
    def __init__(self, api_key=ANTHROPIC_API_KEY, model=MODEL):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def generate_text(self, system_prompt, user_prompt, max_tokens=1524, temperature=0):
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
                            }
                        ]
                    },
                ]
            )
            return message.content[0].text
        except (APIStatusError, APIError) as e:
            logger.error(f"API Error: {str(e)}")
            raise
        except Exception as e:
            logger.exception("Unexpected error in generate_text")
            raise

    def get_model():
        message = "Model is currently set to: {}".format(MODEL)
        
        return self.client._apikey,self.model   # returns the model used for generation and API key





