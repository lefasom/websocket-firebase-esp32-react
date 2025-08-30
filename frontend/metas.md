# Avances realizados y pendientes

## ✅ Avances realizados

### 1. Comunicación
1. **Uso directo de WebSocket**
   - Se probó la interacción directamente con WebSocket para manejar la comunicación en tiempo real.

2. **Uso directo de Firebase**
   - Se intentó realizar toda la interacción directamente con Firebase (Realtime Database / Firestore).

3. **Combinación de WebSocket y Firebase**
   - Se probó integrar ambos, WebSocket y Firebase, trabajando juntos en la comunicación.  
   - **Resultado:** No funcionó correctamente.

### 2. Aplicación
- Aplicación desarrollada en **React Native**.  
- Manejo de **seguridad en archivos de configuración** a través de **variables en `.env`**.  

---

## 🔜 Pendiente de probar (nueva idea)

### 1. Comunicación
4. **WebSocket como capa principal de interacción + Firebase interno**
   - Flujo propuesto:
     - Todas las **interacciones** se gestionan por **WebSocket**.
     - Cuando haya que **editar/guardar datos**, el WebSocket internamente interactúa con **Firebase**.
   - Es decir, **WebSocket envuelve a Firebase**, y no al revés.

### 2. Aplicación
- Verificar que la integración de WebSocket + Firebase mantenga la **seguridad en `.env`**.  
- Asegurar que en React Native el flujo sea **estable** y no se rompa la comunicación.  
