import os
import requests
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

# ========================================================
# 1. Configurações (lidas do .env, com valores padrão)
# ========================================================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "openf1_data")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openf1.org/v1")

# Caso de uso: Corrida do GP da Itália 2023 (Monza)
SESSION_KEY = int(os.getenv("SESSION_KEY", 9159))
MEETING_KEY = int(os.getenv("MEETING_KEY", 1219))


# ========================================================
# 2. Conexão com o MongoDB
# ========================================================
def get_mongo_connection():
    """Lê MONGO_URI do .env, conecta ao MongoDB e retorna o objeto db."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME]


# ========================================================
# 3. Busca de dados na API OpenF1
# ========================================================
def fetch_data(endpoint: str, params: dict) -> list:
    """
    Faz um GET na API OpenF1 e retorna a lista de resultados.
    Em caso de erro, mostra a mensagem e retorna lista vazia.
    """
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"[INFO] {len(data)} registros obtidos de '{endpoint}'.")
        return data
    except (requests.RequestException, ValueError) as e:
        print(f"[ERRO] Falha ao buscar '{endpoint}': {e}")
        return []


# ========================================================
# 4. Armazenamento no MongoDB (sem duplicatas)
# ========================================================
def save_to_collection(data: list, collection_name: str, unique_keys: list):
    """
    Salva os registros na collection usando update_one com upsert=True.
    Se já existir um registro com as mesmas chaves únicas, ele é atualizado
    (não duplica). Assim o script pode rodar várias vezes sem problema.
    """
    if not data:
        print(f"[AVISO] Nada para salvar em '{collection_name}'.")
        return

    try:
        collection = get_mongo_connection()[collection_name]

        for record in data:
            # Monta o filtro com as chaves únicas (ex.: session_key + driver_number)
            query = {key: record.get(key) for key in unique_keys}

            if None in query.values():
                print(f"[AVISO] Registro ignorado (falta chave única): {record}")
                continue

            collection.update_one(query, {"$set": record}, upsert=True)

        print(f"[INFO] {len(data)} registros processados em '{collection_name}'.")
    except PyMongoError as e:
        print(f"[ERRO] Falha ao salvar em '{collection_name}': {e}")


# ========================================================
# 5. Fluxo principal
# ========================================================
def main():
    # 1) Sessão
    sessions = fetch_data("sessions", {"session_key": SESSION_KEY})
    save_to_collection(sessions, "sessions", ["session_key"])

    # 2) Pilotos da sessão
    drivers = fetch_data("drivers", {"session_key": SESSION_KEY})
    save_to_collection(drivers, "drivers", ["session_key", "driver_number"])

    # 3) Voltas da sessão
    laps = fetch_data("laps", {"session_key": SESSION_KEY})
    save_to_collection(laps, "laps", ["session_key", "driver_number", "lap_number"])

    print("[SUCESSO] Coleta finalizada!")


if __name__ == "__main__":
    main()