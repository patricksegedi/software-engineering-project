# src/smarterspeaker/smarthome_client.py

import requests

BACKEND_URL = "http://127.0.0.1:8000"


def control_device(zone: str, device_type: str, action: str):
    """
    AI 스피커에서 존/타입/액션으로 요청할 때
    FastAPI 서버의 /device-control (DB 기반)으로 보내는 함수
    """
    payload = {
        "zone": zone,          # 예: "Living"
        "device_type": device_type,  # 예: "light"
        "action": action,      # 예: "on"
    }

    print(f"[CLIENT] POST /device-control {payload}")
    res = requests.post(f"{BACKEND_URL}/device-control", json=payload, timeout=3)

    try:
        res.raise_for_status()
    except Exception as e:
        print("[CLIENT] device-control error:", e, res.text)
        return None

    return res.json()
