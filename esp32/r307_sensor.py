from r307_uart import send_command
from firebase_utils import send_data, get_data
import time
import urandom

# Constantes para el tiempo de espera
TIMEOUT_SEGUNDOS = 20
PAUSA_CORTA = 0.5  # Pausa entre comandos para estabilidad


def calculate_checksum(packet_data):
    """Calcula el checksum para el paquete de datos del sensor R307."""
    checksum = sum(packet_data)
    return checksum & 0xFFFF  # Asegurarse de que el checksum sea de 2 bytes


def test_connection():
    packet = bytes(
        [
            0xEF,
            0x01,
            0xFF,
            0xFF,
            0xFF,
            0xFF,
            0x01,
            0x00,
            0x03,  # Longitud del paquete corregida
            0x13,
            0x00,
            0x17,  # Checksum corregido
        ]
    )
    response = send_command(packet)
    time.sleep(PAUSA_CORTA)
    return response and len(response) >= 12 and response[9] == 0x00


def obtener_siguiente_posicion():
    """Obtiene la siguiente posición libre en el sensor R307"""
    packet_get_index = bytes(
        [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x1F, 0x00, 0x23]
    )
    response = send_command(packet_get_index)
    time.sleep(1)

    if response and response[9] == 0x00:
        for i in range(256):
            byte_index = 10 + (i // 8)
            bit_position = i % 8
            if byte_index < len(response):
                byte_value = response[byte_index]
                if not ((byte_value >> bit_position) & 1):
                    return i
    return 1


def obtener_posiciones_ocupadas_sensor():
    """Obtiene todas las posiciones ocupadas en el sensor R307"""
    packet_get_index = bytes(
        [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x1F, 0x00, 0x23]
    )
    response = send_command(packet_get_index)
    time.sleep(1)

    posiciones_ocupadas = []
    if response and response[9] == 0x00:
        for i in range(256):
            byte_index = 10 + (i // 8)
            bit_position = i % 8
            if byte_index < len(response):
                byte_value = response[byte_index]
                if (byte_value >> bit_position) & 1:
                    posiciones_ocupadas.append(i)

    return posiciones_ocupadas


def sincronizar_datos():
    """
    Sincroniza los datos del sensor R307 con Firebase.
    Elimina del sensor las huellas que no existen en Firebase.
    """
    print("=== INICIANDO SINCRONIZACIÓN ===")

    # 1. Obtener posiciones ocupadas en el sensor
    posiciones_sensor = obtener_posiciones_ocupadas_sensor()
    print(f"📋 Posiciones en sensor R307: {len(posiciones_sensor)}")

    # 2. Obtener datos de Firebase
    indices_firebase = get_data("indices_sensor")
    if not indices_firebase:
        indices_firebase = {}

    posiciones_firebase = [int(pos) for pos in indices_firebase.keys() if pos.isdigit()]
    print(f"☁️ Posiciones en Firebase: {len(posiciones_firebase)}")

    # 3. Encontrar huellas que están en el sensor pero no en Firebase
    huellas_a_eliminar = []
    for pos in posiciones_sensor:
        if pos not in posiciones_firebase:
            huellas_a_eliminar.append(pos)

    print(f"🗑️ Huellas a eliminar del sensor: {len(huellas_a_eliminar)}")

    # 4. Eliminar huellas del sensor que no están en Firebase
    eliminadas_exitosamente = 0
    errores_eliminacion = 0

    for pos in huellas_a_eliminar:
        print(f"🔄 Eliminando posición {pos} del sensor...")
        if eliminar_huella_del_sensor(pos):
            eliminadas_exitosamente += 1
            print(f"✅ Posición {pos} eliminada exitosamente")
        else:
            errores_eliminacion += 1
            print(f"❌ Error al eliminar posición {pos}")

        # Pequeña pausa entre eliminaciones para estabilidad
        time.sleep(0.5)

    # 5. Verificar sincronización final
    posiciones_sensor_final = obtener_posiciones_ocupadas_sensor()
    huellas_huerfanas = []
    for pos in posiciones_sensor_final:
        if pos not in posiciones_firebase:
            huellas_huerfanas.append(pos)

    # 6. Generar reporte de sincronización
    reporte = {
        "posiciones_sensor_inicial": len(posiciones_sensor),
        "posiciones_firebase": len(posiciones_firebase),
        "huellas_identificadas_eliminar": len(huellas_a_eliminar),
        "huellas_eliminadas_exitosamente": eliminadas_exitosamente,
        "errores_eliminacion": errores_eliminacion,
        "posiciones_sensor_final": len(posiciones_sensor_final),
        "huellas_huerfanas_restantes": len(huellas_huerfanas),
        "sincronizacion_exitosa": len(huellas_huerfanas) == 0,
        "timestamp": generar_timestamp(),
    }

    # 7. Guardar reporte en Firebase
    send_data("sincronizacion/ultimo_reporte", reporte)

    print("=== REPORTE DE SINCRONIZACIÓN ===")
    print(f"📊 Posiciones iniciales en sensor: {reporte['posiciones_sensor_inicial']}")
    print(f"☁️ Posiciones en Firebase: {reporte['posiciones_firebase']}")
    print(f"🗑️ Huellas eliminadas: {reporte['huellas_eliminadas_exitosamente']}")
    print(f"❌ Errores: {reporte['errores_eliminacion']}")
    print(f"📍 Posiciones finales en sensor: {reporte['posiciones_sensor_final']}")
    print(
        f"🔄 Sincronización {'EXITOSA' if reporte['sincronizacion_exitosa'] else 'INCOMPLETA'}"
    )

    if huellas_huerfanas:
        print(f"⚠️ Huellas huérfanas restantes: {huellas_huerfanas}")

    return reporte


def eliminar_huella_del_sensor(id_posicion):
    """
    Elimina una huella específica del sensor R307 por posición.
    No afecta Firebase, solo elimina del sensor.
    """
    pos_high = (id_posicion >> 8) & 0xFF
    pos_low = id_posicion & 0xFF

    data_to_checksum = [0x01, 0x00, 0x07, 0x0C, pos_high, pos_low, 0x00, 0x01]
    checksum = calculate_checksum(data_to_checksum)
    checksum_high = (checksum >> 8) & 0xFF
    checksum_low = checksum & 0xFF

    packet_delete = bytes(
        [
            0xEF,
            0x01,
            0xFF,
            0xFF,
            0xFF,
            0xFF,
            0x01,
            0x00,
            0x07,
            0x0C,
            pos_high,
            pos_low,
            0x00,
            0x01,
            checksum_high,
            checksum_low,
        ]
    )

    response = send_command(packet_delete)
    time.sleep(PAUSA_CORTA)

    return response and response[9] == 0x00


def generar_timestamp():
    """Genera un timestamp simple basado en time.ticks_ms()"""
    return time.ticks_ms()


def wait_for_finger_press(timeout, message,logger):
    """Espera activamente a que un dedo sea colocado en el sensor."""
    print(f"⏳ {message} ({timeout}s)...")
    logger("prueba")
    
    start_time = time.time()
    packet_get_image = bytes(
        [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05]
    )

    while (time.time() - start_time) < timeout:
        response = send_command(packet_get_image)
        if response and response[9] == 0x00:
            print("✅ ¡Huella detectada!")
            
            return True, response
        elif response and response[9] == 0x02:
            time.sleep(PAUSA_CORTA)
        else:
            time.sleep(PAUSA_CORTA)
            
    print("⏰ Tiempo de espera agotado.")
    return False, None


def wait_for_finger_release(timeout, message):
    """Espera activamente a que un dedo sea levantado del sensor."""
    print(f"☝️ {message} ({timeout}s)...")
    if message=='':
       send_data("display", {"mensaje": message})
    
    start_time = time.time()
    packet_get_image = bytes(
        [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05]
    )

    while (time.time() - start_time) < timeout:
        response = send_command(packet_get_image)
        if response and response[9] == 0x02:
            # send_data("display", {"mensaje": "Dedo levantado"})
            print("✅ Dedo levantado.")
            return True
        elif response and response[9] == 0x00:
            time.sleep(PAUSA_CORTA)
        else:
            time.sleep(PAUSA_CORTA)
            
    
    send_data("display", {"mensaje": " Tiempo de espera agotado. El dedo no fue levantado."})
    print("⏰ Tiempo de espera agotado. El dedo no fue levantado.")
    return False


def agregar_huella():
    print("=== AGREGAR NUEVA HUELLA ===")
    posicion = obtener_siguiente_posicion()
    print(f"Usando posición: {posicion}")
    send_data("display", {"mensaje": f"Usando posicion: {posicion}"}) 

    success, _ = wait_for_finger_press(TIMEOUT_SEGUNDOS, "Coloque el dedo")
    if not success:
        return False

    packet1 = bytes(
        [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, 0x01, 0x00, 0x08]
    )
    response = send_command(packet1)
    time.sleep(PAUSA_CORTA)
    if not (response and response[9] == 0x00):
        return False

    if not wait_for_finger_release(TIMEOUT_SEGUNDOS,''):
        return False

    success, _ = wait_for_finger_press(TIMEOUT_SEGUNDOS, "Coloque el dedo nuevamente")
    if not success:
        return False

    packet2 = bytes(
        [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, 0x02, 0x00, 0x09]
    )
    response = send_command(packet2)
    time.sleep(PAUSA_CORTA)
    if not (response and response[9] == 0x00):
        return False

    combine_packet = bytes(
        [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x05, 0x00, 0x09]
    )
    response = send_command(combine_packet)
    time.sleep(PAUSA_CORTA)
    if not (response and response[9] == 0x00):
        return False

    pos_high = (posicion >> 8) & 0xFF
    pos_low = posicion & 0xFF
    data = [0x01, 0x00, 0x06, 0x06, 0x01, pos_high, pos_low]
    checksum = calculate_checksum(data)
    ch = (checksum >> 8) & 0xFF
    cl = checksum & 0xFF

    store_packet = bytes(
        [
            0xEF,
            0x01,
            0xFF,
            0xFF,
            0xFF,
            0xFF,
            0x01,
            0x00,
            0x06,
            0x06,
            0x01,
            pos_high,
            pos_low,
            ch,
            cl,
        ]
    )
    response = send_command(store_packet)
    time.sleep(PAUSA_CORTA)

    if response and response[9] == 0x00:
        timestamp = generar_timestamp()
        usuario_id = f"user_{posicion}_{timestamp}"
        datos_usuario = {
            "id_sensor": posicion,
            "usuario_id": usuario_id,
            "nombre": f"Usuario_{posicion}",
            "apellido": "Pendiente",
            "email": "pendiente@email.com",
            "activo": True,
            "fecha_registro": timestamp,
            "registrado_por": "ESP32",
        }

        if send_data(f"usuarios/{usuario_id}", datos_usuario):
            indice_sensor = {
                "usuario_id": usuario_id,
                "nombre": datos_usuario["nombre"],
                "activo": True,
            }
            send_data(f"indices_sensor/{posicion}", indice_sensor)
            return datos_usuario
        else:
            print("⚠️ Huella guardada pero error al registrar en Firebase")
            return False
    else:
        print("❌ Error al guardar la huella en el sensor.")
        return False


def detectar_huella(logger=print):
    print("=== DETECTAR HUELLA ===")
    # send_data("display", {"mensaje":"Esperando Huella"})
    
    success, _ = wait_for_finger_press(TIMEOUT_SEGUNDOS, "Esperando huella",logger)
    if not success:
        return None

    packet = bytes(
        [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, 0x01, 0x00, 0x08]
    )
    response = send_command(packet)
    time.sleep(PAUSA_CORTA)
    if not (response and response[9] == 0x00):
        return None

    data = [0x01, 0x00, 0x08, 0x04, 0x01, 0x00, 0x00, 0x00, 0x64]
    checksum = calculate_checksum(data)
    ch = (checksum >> 8) & 0xFF
    cl = checksum & 0xFF

    search_packet = bytes(
        [
            0xEF,
            0x01,
            0xFF,
            0xFF,
            0xFF,
            0xFF,
            0x01,
            0x00,
            0x08,
            0x04,
            0x01,
            0x00,
            0x00,
            0x00,
            0x64,
            ch,
            cl,
        ]
    )
    response = send_command(search_packet)
    time.sleep(PAUSA_CORTA)

    if response and response[9] == 0x00:
        id_huella = int.from_bytes(response[10:12], "big")
        score = int.from_bytes(response[12:14], "big")
        indice = get_data(f"indices_sensor/{id_huella}")
        if indice:
            usuario_id = indice.get("usuario_id")
            nombre = indice.get("nombre", "Desconocido")
            activo = indice.get("activo", True)
            timestamp = generar_timestamp()
            datos_acceso = {
                "usuario_id": usuario_id,
                "id_sensor": id_huella,
                "nombre": nombre,
                "timestamp": timestamp,
                "score": score,
                "autorizado": activo,
                "tipo_acceso": "entrada",
            }
            acceso_id = f"acceso_{timestamp}"
            send_data(f"registros_acceso/{acceso_id}", datos_acceso)
            return {"id_sensor": id_huella, "usuario_id": usuario_id, "nombre": nombre}
        else:
            timestamp = generar_timestamp()
            send_data(
                f"intentos_fallidos/{timestamp}",
                {
                    "timestamp": timestamp,
                    "resultado": "no_autorizado",
                    "tipo_acceso": "entrada_denegada",
                },
            )
            return None
    else:
        timestamp = generar_timestamp()
        send_data(
            f"intentos_fallidos/{timestamp}",
            {
                "timestamp": timestamp,
                "resultado": "sin_coincidencia",
                "tipo_acceso": "entrada_denegada",
            },
        )
        return None


# def mostrar_estadisticas():
#     # Estadísticas locales del sensor
#     packet_get_count = bytes(
#         [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x09, 0x00, 0x0D]
#     )
#     response = send_command(packet_get_count)
#     time.sleep(PAUSA_CORTA)
#     if response and response[9] == 0x00:
#         count_sensor = int.from_bytes(response[10:12], "big")
#         print(f"📊 Huellas en sensor R307: {count_sensor}")
#         usuarios_firebase = get_data("usuarios")
#         if usuarios_firebase:
#             count_firebase = len(usuarios_firebase)
#             activos = sum(
#                 1 for u in usuarios_firebase.values() if u.get("activo", True)
#             )
#             print(f"👥 Usuarios en Firebase: {count_firebase}")
#             print(f"✅ Usuarios activos: {activos}")
#             print(f"❌ Usuarios inactivos: {count_firebase - activos}")
#         else:
#             print("📂 Sin usuarios registrados en Firebase")
#     else:
#         print("Error al obtener las estadísticas del sensor.")


def mostrar_posiciones():
    # Posiciones ocupadas en el sensor
    packet_get_index = bytes(
        [0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x1F, 0x00, 0x23]
    )
    response = send_command(packet_get_index)
    time.sleep(1)
    if response and response[9] == 0x00:
        print("🔍 Posiciones ocupadas en sensor:")
        posiciones_ocupadas = []
        for i in range(256):
            if i % 8 == 0:
                byte_index = 10 + (i // 8)
                if byte_index < len(response):
                    byte_value = response[byte_index]
            if (byte_value >> (i % 8)) & 1:
                posiciones_ocupadas.append(i)
        for pos in posiciones_ocupadas[:10]:
            indice = get_data(f"indices_sensor/{pos}")
            if indice:
                nombre = indice.get("nombre", "Sin nombre")
                estado = "🟢" if indice.get("activo", True) else "🔴"
                print(f"   Pos {pos}: {nombre} {estado}")
            else:
                print(f"   Pos {pos}: Sin datos en Firebase")
        if len(posiciones_ocupadas) > 10:
            print(f"   ... y {len(posiciones_ocupadas) - 10} más")
        print(f"Total: {len(posiciones_ocupadas)} posiciones ocupadas")
    else:
        print("Error al obtener las posiciones.")


def eliminar_huella(id_a_eliminar=None):
    if id_a_eliminar is None:
        opcion = input("¿Eliminar huella específica (1) o todas (2)? ")
        if opcion != "1":
            print("❌ Opción no válida")
            return False

        try:
            id_a_eliminar = int(input("ID de la huella a eliminar: "))
        except ValueError:
            print("❌ ID inválido")
            return False

    indice = get_data(f"indices_sensor/{id_a_eliminar}")
    usuario_info = None
    if indice:
        usuario_id = indice.get("usuario_id")
        if usuario_id:
            usuario_info = get_data(f"usuarios/{usuario_id}")

    pos_high = (id_a_eliminar >> 8) & 0xFF
    pos_low = id_a_eliminar & 0xFF

    data_to_checksum = [0x01, 0x00, 0x07, 0x0C, pos_high, pos_low, 0x00, 0x01]
    checksum = calculate_checksum(data_to_checksum)
    checksum_high = (checksum >> 8) & 0xFF
    checksum_low = checksum & 0xFF

    packet_delete = bytes(
        [
            0xEF,
            0x01,
            0xFF,
            0xFF,
            0xFF,
            0xFF,
            0x01,
            0x00,
            0x07,  # Longitud del paquete corregida
            0x0C,
            pos_high,
            pos_low,
            0x00,
            0x01,
            checksum_high,
            checksum_low,  # Checksum calculado
        ]
    )
    response = send_command(packet_delete)
    time.sleep(PAUSA_CORTA)

    if response and response[9] == 0x00:
        print(f"✅ Huella {id_a_eliminar} eliminada del sensor")
        if usuario_info:
            usuario_info["activo"] = False
            usuario_info["fecha_eliminacion"] = generar_timestamp()
            send_data(f"usuarios/{indice['usuario_id']}", usuario_info)
            indice["activo"] = False
            send_data(f"indices_sensor/{id_a_eliminar}", indice)
            print(
                f"✅ Usuario {usuario_info.get('nombre', 'N/A')} desactivado en Firebase"
            )
        else:
            print("⚠️ No se encontró información del usuario en Firebase")
        return True
    else:
        print("❌ Error al eliminar la huella del sensor")
        return False