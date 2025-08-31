# firebase_utils.py

import urequests
import ujson

FIREBASE_URL = "https://esp32-a8053-default-rtdb.firebaseio.com"


def send_data(path, data):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        response = urequests.put(url, data=ujson.dumps(data))
        response.close()
        print("📤 Datos enviados correctamente")
        return True
    except Exception as e:
        print("❌ Error al enviar datos:", e)
        return False


def get_data(path, silent=False):
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        response = urequests.get(url)
        data = response.json()
        response.close()
        if not silent:
            print("📥 Datos recibidos correctamente")
        return data
    except Exception as e:
        if not silent:
            print("❌ Error al obtener datos:", e)
        return None
