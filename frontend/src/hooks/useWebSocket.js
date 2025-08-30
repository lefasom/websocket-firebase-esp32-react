import { useState, useEffect, useRef } from 'react';

const WEBSOCKET_URL = 'ws://192.168.100.15:80'; 
const RECONNECT_TIMEOUT = 3000; 
const PING_INTERVAL = 30000; 
const PONG_TIMEOUT = 5000; 

export function useWebSocket() {
    const [messages, setMessages] = useState([]);
    const [socket, setSocket] = useState(null);
    const [status, setStatus] = useState('Desconectado');

    const pingIntervalRef = useRef(null);
    const pongTimeoutRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const isReconnectingRef = useRef(false);

    const clearAllTimers = () => {
        if (pingIntervalRef.current) {
            clearInterval(pingIntervalRef.current);
            pingIntervalRef.current = null;
        }
        if (pongTimeoutRef.current) {
            clearTimeout(pongTimeoutRef.current);
            pongTimeoutRef.current = null;
        }
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }
    };

    const sendPing = (ws) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
            pongTimeoutRef.current = setTimeout(() => {
                ws.close();
            }, PONG_TIMEOUT);
        }
    };

    const handlePong = () => {
        if (pongTimeoutRef.current) {
            clearTimeout(pongTimeoutRef.current);
            pongTimeoutRef.current = null;
        }
    };

    const startPingPong = (ws) => {
        if (pingIntervalRef.current) {
            clearInterval(pingIntervalRef.current);
        }
        pingIntervalRef.current = setInterval(() => {
            sendPing(ws);
        }, PING_INTERVAL);
    };

    useEffect(() => {
        const connect = () => {
            if (isReconnectingRef.current) return;

            setStatus('Conectando...');
            isReconnectingRef.current = true;

            const ws = new WebSocket(WEBSOCKET_URL);

            ws.onopen = () => {
                setStatus('Conectado');
                setSocket(ws);
                isReconnectingRef.current = false;
                startPingPong(ws);
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'pong') {
                        handlePong();
                        return;
                    }
                    setMessages(prev => [...prev, event.data]);
                } catch {
                    setMessages(prev => [...prev, event.data]);
                }
            };

            ws.onclose = (event) => {
                setStatus('Desconectado');
                setSocket(null);
                clearAllTimers();

                if (event.code !== 1000) {
                    isReconnectingRef.current = false;
                    reconnectTimeoutRef.current = setTimeout(connect, RECONNECT_TIMEOUT);
                } else {
                    isReconnectingRef.current = false;
                }
            };

            ws.onerror = () => {
                setStatus('Error');
                isReconnectingRef.current = false;
            };
        };

        connect();

        return () => {
            clearAllTimers();
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close(1000, 'Componente desmontado');
            }
        };
    }, []);

    const sendMessage = (msg) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'message', content: msg }));
        }
    };

    return { status, messages, sendMessage };
}
