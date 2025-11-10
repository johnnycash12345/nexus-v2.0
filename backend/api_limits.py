# Limites Diarios (Requests Per Day - RPD) para planos Gratuitos
FREE_LIMITS = {
    "tavily": 30,         # Free tier e ~1000/mes, entao aprox 30/dia para ser seguro
    "serpapi": 3,         # Free tier e 100/mes, muito baixo, aprox 3/dia
    "bing_search": 160,   # Free tier e ~5000/mes
    "google_custom": 100, # 100/dia gratuito
    "newsapi": 100,       # Developer plan e 100/dia
    "gnews": 100,         # Aprox 100/dia
    "currents": 600,      # 600/dia no plano free
    "google_gemini": 1500, # Gemini 1.5 Flash tem 1500 RPD gratis
    "groq": 14400,         # Groq tem limites altos no free tier
    "huggingface": 1000,   # Placeholder seguro
    "openweathermap": 1000, # 1000 chamadas/dia gratis
    "nasa": 950,            # Limitando a 950/dia por seguranca
    "alphavantage": 25,     # 25/dia no plano free
}

def get_limit(service_name: str) -> int:
    """Retorna o limite diario para um servico, ou 0 se desconhecido.
    """
    return FREE_LIMITS.get(service_name.lower(), 0)
