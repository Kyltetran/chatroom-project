import React from "react";
import { FiLogOut } from "react-icons/fi";

function TopBar({ onLeave }) {
  return (
    <div
      className="flex justify-between items-center px-6 py-3 backdrop-blur-md"
      style={{
        backgroundColor: "rgba(255, 255, 255, 0.7)",
        boxShadow: `
          0px 0px 2.15px rgba(0, 0, 0, 0.2),
          0px 0px 4.29px rgba(0, 0, 0, 0.05)
        `,
      }}
    >
      <h1
        className="text-xl font-semibold"
        style={{
          color: "black",
          fontFamily: "'Roboto', sans-serif",
        }}
      >
        FUV Chatroom
      </h1>
      <button
        onClick={onLeave}
        className="flex items-center justify-center text-white hover:bg-red-500 transition duration-300"
        style={{
          backgroundColor: "#EF4444",
          borderRadius: "50%",
          width: "40px",
          height: "40px",
        }}
        title="Leave chat"
      >
        <FiLogOut size={20} />
      </button>
    </div>
  );
}

export default TopBar;