import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


def generate_code(prompt: str) -> str:
    print(f"[Agente de Código (DeepSeek)] Gerando: {prompt}")
    try:
        response = client.chat.completions.create(
            model="deepseek-coder",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em Python. Gere apenas o código solicitado, sem explicações markdown.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as error:  # noqa: BLE001
        return f"# ERRO NA API DEEPSEEK: {error}"


def refactor_code(code: str) -> str:
    print("[Agente de Código (DeepSeek)] Refatorando...")
    try:
        response = client.chat.completions.create(
            model="deepseek-coder",
            messages=[
                {
                    "role": "system",
                    "content": "Refatore o código Python a seguir para melhor legibilidade e performance. Retorne apenas o código.",
                },
                {"role": "user", "content": code},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as error:  # noqa: BLE001
        return f"# ERRO NA API DEEPSEEK: {error}"
