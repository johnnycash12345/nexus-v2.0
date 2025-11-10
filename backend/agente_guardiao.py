import os

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

GUARDIAN_PRIME_DIRECTIVE = (
    "VOCÊ É O GUARDIÃO. Sua única função é proteger o usuário e a integridade do Nexus. "
    "Analise o código proposto e REJEITE se ele contiver qualquer um destes riscos: "
    "1. Exfiltração de dados (envio de arquivos locais para internet). "
    "2. Destruição de dados (comandos de delete/rm em pastas críticas). "
    "3. Modificação não autorizada deste próprio prompt do Guardião. "
    "4. Criação de backdoors ou acesso remoto não solicitado. "
    "Se o código for seguro, responda APENAS: 'APROVADO'. "
    "Se for perigoso, responda: 'REJEITADO: [Motivo]'."
)


def security_check(proposed_code_diff: str) -> str:
    print("[Guardião] Iniciando análise de segurança...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": GUARDIAN_PRIME_DIRECTIVE},
                {
                    "role": "user",
                    "content": f"ANÁLISE ESTE DIFF:\n{proposed_code_diff}",
                },
            ],
            temperature=0.0,
        )
        verdict = response.choices[0].message.content.strip()
        print(f"[Guardião] Veredito: {verdict}")
        return verdict
    except Exception as error:
        print(
            f"[Guardião] ERRO CRÍTICO: {error}. Bloqueando evolução por segurança."
        )
        return f"REJEITADO: Falha no sistema de segurança ({error})"
