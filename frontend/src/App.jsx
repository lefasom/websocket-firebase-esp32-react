import React from 'react';
import PingPong from './components/PingPong';
import WebSocketUI from './components/WebSocketUI';

function App() {
  return (
    <PingPong>
      {({ status, messages, sendMessage }) => (
        <WebSocketUI 
          status={status} 
          messages={messages} 
          onSend={sendMessage} 
        />
      )}
    </PingPong>
  );
}

export default App;
