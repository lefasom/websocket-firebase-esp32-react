# main.py

# Importa las librerías necesarias para la red y el socket
import network
import usocket as socket
from time import sleep
import machine

# Importa el nuevo módulo que se llama 'websocket'
import websocket

# --- Sección de configuración ---
# Aquí puedes cambiar la red a la que se conectará el ESP32
ssid = "HUAWEI-2.4G-94Df"
password = "xqTKH4X5"

# Puerto en el que el servidor WebSocket escuchará
port = 80

# --- Sección de conexión Wi-Fi ---
# Configura el ESP32 en modo estación (STA_IF) para que se conecte a un router.
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

print('Conectando a la red...')
# Espera hasta que la conexión a la red sea exitosa
while not station.isconnected():
    print('.', end='')
    sleep(1)

ip_address = station.ifconfig()[0]
print('\nConectado a la IP:', ip_address)

# --- Sección de configuración del servidor TCP/IP ---
# Crea un objeto socket TCP/IP.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Permite que el puerto se reutilice inmediatamente después de cerrar el programa.
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Asocia el socket a todas las interfaces de red ('') en el puerto 80.
s.bind(('', port))
# Pone el servidor en modo de escucha para aceptar conexiones.
s.listen(1)
print('Servidor WebSocket escuchando en el puerto', port)

# --- Bucle principal del servidor ---
# Este bucle corre indefinidamente, esperando nuevas conexiones.
while True:
    try:
        # Acepta una nueva conexión entrante de un cliente.
        conn, addr = s.accept()
        print('Conexión TCP aceptada desde', addr)
        
        # Llama a la función para manejar el protocolo WebSocket.
        websocket.handle_websocket_connection(conn)

    except Exception as e:
        # Manejo de errores en caso de que algo falle en el socket principal.
        print('Error del servidor:', e)
        sleep(1)