import { useWebSocket } from '../hooks/useWebSocket';

function PingPong({ children }) {
  const { status, messages, sendMessage } = useWebSocket();

  // 👉 Pasamos lo necesario a los hijos
  return children({ status, messages, sendMessage });
}

export default PingPong;
