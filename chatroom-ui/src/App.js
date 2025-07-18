import React, { useState, useEffect } from "react";
import TopBar from "./components/TopBar";
import UserList from "./components/UserList";
import ChatArea from "./components/ChatArea";
import InputArea from "./components/InputArea";
import WelcomeWindow from "./components/WelcomeWindow";
import dayjs from "dayjs";

let ws; // We define outside so we can reuse it

function App() {
  const [messages, setMessages] = useState([]);
  const [users, setUsers] = useState([]);
  const [myName, setMyName] = useState("");
  const [connected, setConnected] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    if (!connected) return;

    ws.onopen = () => {
      console.log("[WS] Connected to Python client.py");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (["public", "private", "system"].includes(data.type)) {
        setMessages((prev) => [
          ...prev,
          {
            id: prev.length + 1,
            user: data.user,
            text: data.text,
            timestamp: data.timestamp || dayjs().toISOString(),
            system: data.system || false,
          },
        ]);

        // Check system messages to update active users
        if (data.type === "system") {
          const text = data.text.toLowerCase();
          if (text.includes("has joined")) {
            const newUser = data.user;
            setUsers((prev) => [...new Set([...prev, newUser])]);
          } else if (text.includes("has left")) {
            const leftUser = data.user;
            setUsers((prev) => prev.filter((u) => u !== leftUser));
          }
        }
      }
    };

    ws.onclose = () => {
      console.log("[WS] Connection closed");
      setConnected(false);
    };

    ws.onerror = (err) => {
      console.error("[WS] Error:", err);
      setConnected(false);
    };
  }, [connected]);

  const handleSend = (text) => {
    if (!connected) return;
    ws.send(text);
  };

  const handleLeave = () => {
    if (connected) {
      ws.close();
      setConnected(false);
    }
    setMessages((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        user: "System",
        text: `${myName} left the chat`,
        system: true,
        timestamp: dayjs().toISOString(),
      },
    ]);
  };

  const handleJoin = (username) => {
    if (!username.trim()) {
      alert("Please enter your name to join");
      return;
    }
    setMyName(username);
    setShowWelcome(false);

    // Open WebSocket connection
    ws = new WebSocket("ws://localhost:6789");
    ws.onopen = () => {
      console.log("[WS] Connected to client.py");
    
      // Send init message
      ws.send(JSON.stringify({
        type: "init",
        username: username
      }));
    };
    setConnected(true);
  };

  if (showWelcome) {
    return <WelcomeWindow onJoin={handleJoin} />;
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <UserList users={users} myName={myName} />
      <div className="flex flex-col flex-1">
        <TopBar onLeave={handleLeave} />
        <ChatArea messages={messages} />
        <InputArea onSend={handleSend} disabled={!connected} />
      </div>
    </div>
  );
}

export default App;
