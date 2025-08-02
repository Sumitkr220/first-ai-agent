import os
from openai import OpenAI

# You can set your OpenAI API key as an environment variable or paste it here
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")
    return OpenAI(api_key=api_key)

def ask_country_count():
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How many countries are there in the world?"}
        ]
    )
    answer = response.choices[0].message.content.strip()
    print("OpenAI response:", answer)

if __name__ == "__main__":
    ask_country_count()