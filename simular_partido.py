import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

def main():
    print("Iniciando simulación del Prode...")

    # 1. Crear usuarios
    print("\n--- Creando usuarios ---")
    users = ["MiUsuario", "Martin", "Sofi"]
    user_ids = {}
    
    for username in users:
        response = requests.post(f"{BASE_URL}/users/", json={"username": username})
        if response.status_code == 201:
            data = response.json()
            user_ids[username] = data["id"]
            print(f"[OK] Usuario creado: {username} (ID: {data['id']})")
        elif response.status_code == 400 and "ya está registrado" in response.text:
            print(f"[WARNING] Usuario {username} ya existe, obteniendo ID del ranking...")
            ranking = requests.get(f"{BASE_URL}/users/ranking").json()
            for u in ranking:
                if u["username"] == username:
                    user_ids[username] = u["id"]
                    break
        else:
            print(f"[ERROR] Error al crear usuario {username}: {response.text}")

    # Usar los IDs devueltos por la API (por defecto 1, 2, 3 si hay fallos pero asumimos éxito)
    my_id = user_ids.get("MiUsuario", 1)
    martin_id = user_ids.get("Martin", 2)
    sofi_id = user_ids.get("Sofi", 3)

    # 2. Crear partido
    print("\n--- Creando partido ---")
    match_data = {
        "team_home": "Argentina",
        "team_away": "Polonia",
        "match_date": datetime.utcnow().isoformat() + "Z",
        "phase": "Grupos"
    }
    response = requests.post(f"{BASE_URL}/matches/", json=match_data)
    if response.status_code in [200, 201]:
        match = response.json()
        match_id = match["id"]
        print(f"[OK] Partido creado: Argentina vs Polonia (ID: {match_id})")
    else:
        print(f"[ERROR] Error al crear partido: {response.text}")
        return

    # 3. Enviar predicciones
    print("\n--- Enviando predicciones ---")
    predictions = [
        {"user_id": my_id, "match_id": match_id, "score_home_predicted": 2, "score_away_predicted": 0, "name": "MiUsuario"},
        {"user_id": martin_id, "match_id": match_id, "score_home_predicted": 2, "score_away_predicted": 1, "name": "Martin"},
        {"user_id": sofi_id, "match_id": match_id, "score_home_predicted": 1, "score_away_predicted": 1, "name": "Sofi"},
    ]

    for p in predictions:
        pred_data = {
            "user_id": p["user_id"],
            "match_id": p["match_id"],
            "score_home_predicted": p["score_home_predicted"],
            "score_away_predicted": p["score_away_predicted"]
        }
        response = requests.post(f"{BASE_URL}/predictions/", json=pred_data)
        if response.status_code in [200, 201]:
            print(f"[OK] Predicción de {p['name']} enviada: {p['score_home_predicted']} - {p['score_away_predicted']}")
        else:
            print(f"[ERROR] Error al enviar predicción de {p['name']}: {response.text}")

    # 4. Resolver el partido
    print("\n--- Resolviendo partido ---")
    resolve_data = {
        "score_home_actual": 2,
        "score_away_actual": 0
    }
    response = requests.put(f"{BASE_URL}/matches/{match_id}/resolve", json=resolve_data)
    if response.status_code in [200, 201]:
        print("[OK] Partido resuelto con resultado: Argentina 2 - 0 Polonia")
    else:
        print(f"[ERROR] Error al resolver el partido: {response.text}")

    # 5. Obtener e imprimir el ranking final
    print("\n--- Ranking Final ---")
    response = requests.get(f"{BASE_URL}/users/ranking")
    if response.status_code == 200:
        ranking = response.json()
        print(f"{'Pos.':<5} | {'Usuario':<15} | {'Puntos'}")
        print("-" * 35)
        for idx, user in enumerate(ranking, 1):
            print(f"{idx:<5} | {user['username']:<15} | {user['total_points']}")
    else:
        print(f"[ERROR] Error al obtener el ranking: {response.text}")

if __name__ == "__main__":
    main()
