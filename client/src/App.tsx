import { useEffect, useState } from 'react';
import { socket } from './env';
import './style/css/App.css';

export default function App() {


  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
    }

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
    };
  }, []);

  function toggleConnection() {
    if (isConnected)
      socket.disconnect();
    else
      socket.connect();
  }

  return (
    <>
      <h1>Welcome to Color Conquerer</h1>
      <button className="start-button" onClick={toggleConnection}>
        {isConnected ? "Disconnect" : "Connect"}
      </button>
    </>
  )
}
