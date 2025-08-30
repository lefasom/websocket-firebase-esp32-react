# websocket.py

# Importa las librerías necesarias para el protocolo WebSocket
import hashlib
import ubinascii as binascii
import struct
import ujson as json

def handle_websocket_connection(conn):
    """
    Función principal para manejar una conexión WebSocket.
    Se encarga del handshake y luego entra en un bucle para recibir mensajes.
    """
    try:
        # --- Paso 1: El WebSocket Handshake ---
        # Lee la primera solicitud HTTP del cliente.
        request = conn.recv(1024).decode('utf-8')
        
        # Verifica si es una solicitud de WebSocket (handshake).
        if "Upgrade: websocket" in request and "Connection: Upgrade" in request:
            # Extrae la clave especial que el cliente envía para el handshake.
            key_start = request.find("Sec-WebSocket-Key:") + len("Sec-WebSocket-Key:")
            key_end = request.find("\r\n", key_start)
            client_key = request[key_start:key_end].strip()

            # Genera la clave de respuesta usando SHA1 y Base64.
            guid = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            handshake_input = (client_key + guid).encode('utf-8')
            sha1_hash = hashlib.sha1(handshake_input)
            response_key = binascii.b2a_base64(sha1_hash.digest()).decode('utf-8').strip()

            # Construye y envía la respuesta al cliente.
            response_headers = "HTTP/1.1 101 Switching Protocols\r\n"
            response_headers += "Upgrade: websocket\r\n"
            response_headers += "Connection: Upgrade\r\n"
            response_headers += "Sec-WebSocket-Accept: {}\r\n".format(response_key)
            response_headers += "\r\n"
            conn.send(response_headers.encode('utf-8'))
            
            print("Handshake completado. Conexión WebSocket establecida.")

            # --- Paso 2: Bucle para recibir y procesar mensajes ---
            while True:
                # Llama a la función para leer el siguiente mensaje del socket.
                message = read_websocket_message(conn)
                if message is None:
                    # Si la función devuelve None, significa que la conexión se cerró.
                    break
                
                # Procesa el mensaje recibido
                handle_message(conn, message)
                
        else:
            conn.close()
            print("Conexión no es un WebSocket. Cerrada.")

    except Exception as e:
        print("Error en la conexión WebSocket:", e)
    finally:
        # Aquí cerramos la conexión solo cuando el bucle 'while True' de la
        # conexión ha finalizado o ha ocurrido un error.
        conn.close()
        print('Conexión TCP cerrada.')

def read_websocket_message(conn):
    """
    Lee y decodifica un mensaje completo del socket WebSocket.
    """
    try:
        # Lee los primeros 2 bytes del encabezado del frame.
        header = conn.recv(2)
        if not header:
            return None # Si no hay datos, la conexión se cerró.

        byte1, byte2 = struct.unpack('!BB', header)
        
        # Extrae el opcode (tipo de mensaje) y la bandera de máscara.
        opcode = byte1 & 0x0f
        mask = bool(byte2 & 0x80)
        
        # Extrae la longitud de los datos.
        length = byte2 & 0x7f

        # Si la longitud es un valor especial, lee bytes adicionales.
        if length == 126:
            length = struct.unpack('!H', conn.recv(2))[0]
        elif length == 127:
            length = struct.unpack('!Q', conn.recv(8))[0]
            
        # Lee la máscara de 4 bytes si el mensaje está enmascarado.
        mask_bits = conn.recv(4) if mask else None
        
        # Lee los datos del mensaje.
        data = conn.recv(length)
        
        # Aplica la máscara a los datos si es necesario.
        if mask and data:
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))
            
        # Retorna el mensaje decodificado.
        if opcode == 0x1: # Si es un mensaje de texto
            return data.decode('utf-8')
        elif opcode == 0x8: # Si el cliente envió un 'close frame'
            return None
        
    except Exception as e:
        print("Error al leer el mensaje:", e)
        return None

def handle_message(conn, message):
    """
    Procesa un mensaje recibido del cliente.
    Aquí puedes añadir tu lógica (ej. controlar un LED, enviar un dato a un sensor).
    """
    try:
        print("Mensaje recibido:", message)
        
        # Intenta parsear como JSON para manejar ping-pong
        try:
            data = json.loads(message)
            
            if data.get('type') == 'ping':
                print("📡 Ping recibido, enviando pong...")
                # Responde con pong
                pong_response = json.dumps({'type': 'pong'})
                send_websocket_message(conn, pong_response)
                
            elif data.get('type') == 'message':
                print("💌 Mensaje de usuario:", data.get('content', ''))
                # Aquí puedes agregar tu lógica para manejar mensajes del usuario
                
                # Ejemplo: responder al cliente
                response = json.dumps({
                    'type': 'response', 
                    'content': 'Mensaje recibido: ' + str(data.get('content', ''))
                })
                send_websocket_message(conn, response)
                
            else:
                print("Tipo de mensaje desconocido:", data.get('type'))
                
        except:
            # Si no es JSON válido, trata como mensaje normal
            print("Mensaje de texto simple:", message)
            
            # Respuesta de eco
            response = "ESP32 recibió: " + message
            send_websocket_message(conn, response)
            
    except Exception as e:
        print("Error al manejar mensaje:", e)

def send_websocket_message(conn, message):
    """
    Envía un mensaje a través del WebSocket usando el formato de frame correcto.
    """
    try:
        # Convierte el mensaje a bytes
        message_bytes = message.encode('utf-8')
        message_length = len(message_bytes)
        
        # Construye el header del frame
        # Byte 1: FIN=1, RSV=000, Opcode=0001 (text frame)
        byte1 = 0x81
        
        # Byte 2 y longitud
        if message_length <= 125:
            header = struct.pack('!BB', byte1, message_length)
        elif message_length <= 65535:
            header = struct.pack('!BBH', byte1, 126, message_length)
        else:
            header = struct.pack('!BBQ', byte1, 127, message_length)
        
        # Envía header + mensaje
        conn.send(header + message_bytes)
        print("📤 Mensaje enviado:", message)
        
    except Exception as e:
        print("Error al enviar mensaje:", e)