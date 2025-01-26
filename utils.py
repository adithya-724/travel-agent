from langchain_openai import OpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


def get_deepseek_response(system_msg,human_msg):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": human_msg},
        ],
        stream=False
    )
    return response.choices[0].message.content