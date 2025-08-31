function WebSocketUI({ status, messages, onSend }) {
  const handleSend = (e) => {
    const msg = e;
    onSend(msg);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>WebSocket con ESP32 y React (Ping-Pong)</h1>
      <p>Estado: <strong>{status}</strong></p>
      <p>Asegúrate de que tu computadora y el ESP32 estén en la misma red Wi-Fi.</p>
      <button 
        onClick={()=>handleSend("agregar_huella")} 
        disabled={status !== 'Conectado'}
        style={{
          padding: '10px 20px', 
          fontSize: '16px', 
          cursor: status === 'Conectado' ? 'pointer' : 'not-allowed'
        }}
      >
       AGREGAR
      </button>
         <button 
        onClick={()=>handleSend("detectar_huella")} 
        disabled={status !== 'Conectado'}
        style={{
          padding: '10px 20px', 
          fontSize: '16px', 
          cursor: status === 'Conectado' ? 'pointer' : 'not-allowed'
        }}
      >
        DETECTAR
      </button>
      <hr />
      <h2>Mensajes Recibidos:</h2>
      <ul style={{ listStyleType: 'none', padding: 0 }}>
        {messages.map((msg, index) => (
          <li key={index} style={{
            padding: '8px', 
            borderBottom: '1px solid #eee'
          }}>
            {msg}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default WebSocketUI;
