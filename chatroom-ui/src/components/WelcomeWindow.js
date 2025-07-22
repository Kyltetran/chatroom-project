import React, { useState } from "react";

const { ipcRenderer } = window.require("electron");

function WelcomeWindow({ onJoin }) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleJoin = () => {
    if (!name.trim()) {
      setError("Please enter your name to join");
      return;
    }

    const trimmedName = name.trim();
    ipcRenderer.send("start-client", trimmedName); // ✅ send to main process
    onJoin(trimmedName); // ✅ continue with UI logic
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-white">
      {/* Title */}
      <h1
        style={{
          fontFamily: "'Roboto', sans-serif",
          color: "#0E6E3B",
          fontSize: "36px",
          marginBottom: "40px",
        }}
      >
        Welcome to FUV Chatroom
      </h1>

      {/* Input triangle */}
      <div
        className="flex items-center justify-center"
        style={{
          width: "612px",
          height: "95px",
          backgroundColor: "#F5F5F5",
          borderRadius: "80px",
          border: "1px solid #959494",
          marginBottom: "20px",
        }}
      >
        <input
          type="text"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => {
            setName(e.target.value);
            setError("");
          }}
          style={{
            width: "90%",
            height: "70%",
            backgroundColor: "transparent",
            border: "none",
            outline: "none",
            textAlign: "center",
            fontFamily: "'Roboto', sans-serif",
            fontSize: "24px",
            color: "#696969",
          }}
        />
      </div>

      {/* Error */}
      {error && (
        <p
          style={{
            color: "#D13030",
            fontFamily: "'Roboto', sans-serif",
            marginBottom: "10px",
          }}
        >
          {error}
        </p>
      )}

      {/* Join button */}
      <button
        onClick={handleJoin}
        style={{
          width: "180px",
          height: "85px",
          backgroundColor: "rgba(203, 239, 207, 0.55)",
          borderRadius: "80px",
          border: "none",
          fontFamily: "'Roboto', sans-serif",
          fontSize: "24px",
          color: "black",
          cursor: "pointer",
        }}
      >
        Join
      </button>
    </div>
  );
}

export default WelcomeWindow;
