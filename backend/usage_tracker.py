import json
import os
from datetime import datetime

from api_limits import get_limit

TRACKER_FILE = 'daily_usage.json'


def _load_usage() -> dict:
    if not os.path.exists(TRACKER_FILE):
        return {"date": datetime.now().strftime("%Y-%m-%d"), "counts": {}}
    try:
        with open(TRACKER_FILE, 'r') as file_handle:
            data = json.load(file_handle)
        if data.get('date') != datetime.now().strftime('%Y-%m-%d'):
            return {"date": datetime.now().strftime("%Y-%m-%d"), "counts": {}}
        return data
    except Exception:
        return {"date": datetime.now().strftime("%Y-%m-%d"), "counts": {}}


def _save_usage(data: dict):
    with open(TRACKER_FILE, 'w') as file_handle:
        json.dump(data, file_handle)


def can_use_api(service_name: str) -> bool:
    """Verifica se ainda temos orcamento para usar esta API hoje."""
    data = _load_usage()
    limit = get_limit(service_name)
    if limit == 0:
        return True
    current_usage = data['counts'].get(service_name, 0)
    if current_usage >= limit:
        print(f"[Usage Tracker] BLOQUEADO: Limite diario atingido para {service_name} ({current_usage}/{limit})")
        return False
    return True


def track_usage(service_name: str):
    """Registra +1 uso para o servico especificado."""
    data = _load_usage()
    data['counts'][service_name] = data['counts'].get(service_name, 0) + 1
    _save_usage(data)
    limit = get_limit(service_name)
    if limit > 0:
        print(f"[Usage Tracker] {service_name}: {data['counts'][service_name]}/{limit} usados hoje.")
