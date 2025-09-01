from openai import AsyncOpenAI, OpenAIError

from src.config import OPENAI_API_KEY

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



class OpenAiClient:
    def __init__(self):
        self._client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def ask(self, user_message: str, system_prompt: str = "You are a helpful assistant") -> str:
        try:
            response = await self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            logging.error(f"Error in ask: {e}")
            raise

    async def ask_photo(self, b64_str: str, system_prompt: str = "Please, describe this photo in Ukrainian") -> str:
        try:
            # Відправляємо в OpenAI
            response = await self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_str}"}}
                    ]}
                ]
            )

            return response.choices[0].message.content
        except OpenAIError as e:
            logging.error(f"Error in ask_photo: {e}")
            raise
