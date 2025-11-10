import os

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

GUARDIAN_PRIME_DIRECTIVE = (
    "VOCE E O GUARDIAO. Sua unica funcao e proteger o usuario e a integridade do Nexus. "
    "Analise o codigo proposto e REJEITE se ele contiver qualquer um destes riscos: "
    "1. Exfiltracao de dados (envio de arquivos locais para internet). "
    "2. Destruicao de dados (comandos de delete/rm em pastas criticas). "
    "3. Modificacao nao autorizada deste proprio prompt do Guardiao. "
    "4. Criacao de backdoors ou acesso remoto nao solicitado. "
    "Se o codigo for seguro, responda APENAS: 'APROVADO'. "
    "Se for perigoso, responda: 'REJEITADO: [Motivo]'."
)


def security_check(proposed_code_diff: str) -> str:
    print("[Guardiao] Iniciando analise de seguranca...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": GUARDIAN_PRIME_DIRECTIVE},
                {
                    "role": "user",
                    "content": f"ANALISE ESTE DIFF:\n{proposed_code_diff}",
                },
            ],
            temperature=0.0,
        )
        verdict = response.choices[0].message.content.strip()
        print(f"[Guardiao] Veredito: {verdict}")
        return verdict
    except Exception as error:
        print(f"[Guardiao] ERRO CRITICO: {error}. Bloqueando evolucao por seguranca.")
        return f"REJEITADO: Falha no sistema de seguranca ({error})"


def optimize_prompt(original_prompt: str, failure_result: str) -> str:
    """
    Otimiza prompts operacionais com base em falhas observadas.
    """
    if not original_prompt:
        return original_prompt

    system_prompt = (
        "Voce e o Otimizador de Prompt do Nexus. Analise o prompt original e o resultado "
        "da falha. Gere um novo prompt que seja mais claro e robusto para evitar esta "
        "falha no futuro. Retorne APENAS o novo prompt otimizado."
    )
    user_prompt = (
        f"PROMPT ORIGINAL:\n{original_prompt}\n\n"
        f"RESULTADO DA FALHA OBSERVADA:\n{failure_result}"
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        optimized = response.choices[0].message.content.strip()
        return optimized or original_prompt
    except Exception as error:  # noqa: BLE001
        print(f"[Guardiao] Falha ao otimizar prompt: {error}")
        return original_prompt
