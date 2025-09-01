import img1 from '../assets/detectar.png';
import img2 from '../assets/guardar.png';

function WebSocketUI({ status, messages, onSend }) {
  const handleSend = (e) => {
    const msg = e;
    onSend(msg);
  };

  return (
    <div
      style={{
        padding: "20px",
        fontFamily: "Arial, sans-serif",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "20px",
      }}
    >
      {/* Simulación de display */}
      <div
        style={{
          backgroundColor: "#111",
          fontFamily: "monospace",
          width: "300px",
          height: "110px",
          border: "1px solid #0f0",
          padding: "20px",
          overflowY: "auto",
        }}
      >
        <p
          style={{
          fontSize:"17px",
          color: "rgba(20, 175, 226, 1)",

        }}>
          Estado: <strong>{status}</strong>
        </p>
        <p style={{
          fontSize:"17px",
          color: "#0f0",

        }}>
          {messages.map((msg, index) => (
            <span
              key={index}
            >
              {msg}
            </span>
          ))}
        </p>
      </div>

      {/* Botones estilo touch */}
      <div
        style={{
          display: "flex",
          gap: "80px",
        }}
      >
        <div style={{
            // Tamaño fijo para el círculo
          
           
            display: "flex",
            flexDirection:'column',
            justifyContent: "center",
            alignItems: "center",
          }}>
        <button
              onClick={() => handleSend("agregar_huella")}
          disabled={status !== "Conectado"}
          style={{
            // Tamaño fijo para el círculo
            width: "60px",
            height: "60px",
            // Elimina el padding para que la imagen se adapte
            padding: "0",
            borderRadius: "50%",
                      border: "2px solid #0f0",

            backgroundColor: status === "Conectado" ? "#444" : "#999",
            cursor: status === "Conectado" ? "pointer" : "not-allowed",
            boxShadow: "0 4px #222, inset 0 0 10px rgba(0,0,0,0.5)",
            transition: "transform 0.1s ease",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
          onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.9)")}
          onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <img
            src={img2}
            alt="guardar huella"
            style={{
              // La imagen ocupa todo el espacio del botón
              width: "100%",
              height: "100%",
              borderRadius: "50%", // Asegura que la imagen también sea redonda
              objectFit: "cover", // Esto es clave para que la imagen no se distorsione
            }}
          />
        </button>
            <p>Agregar huella</p>
</div>
        <div style={{
            // Tamaño fijo para el círculo
          
            display: "flex",
            flexDirection:'column',
            justifyContent: "center",
            alignItems: "center",
          }}>

       <button
            onClick={() => handleSend("detectar_huella")}
            disabled={status !== "Conectado"}
            style={{
            // Tamaño fijo para el círculo
            width: "60px",
            height: "60px",
            // Elimina el padding para que la imagen se adapte
            padding: "0",
            borderRadius: "50%",
          border: "2px solid #0f0",
            backgroundColor: status === "Conectado" ? "#444" : "#999",
            cursor: status === "Conectado" ? "pointer" : "not-allowed",
            boxShadow: "0 4px #222, inset 0 0 10px rgba(0,0,0,0.5)",
            transition: "transform 0.1s ease",
            display: "fle x",
            justifyContent: "center",
            alignItems: "center",
          }}
            onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.9)")}
            onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <img
            src={img1}
            alt="detectar huella"
            style={{
              // La imagen ocupa todo el espacio del botón
              width: "100%",
              height: "100%",
              borderRadius: "50%", // Asegura que la imagen también sea redonda
              objectFit: "cover", // Esto es clave para que la imagen no se distorsione
            }}
          />
        </button>
            <p>Detectar huella</p>
        </div>

      </div>
    </div>
  );
}

export default WebSocketUI;
