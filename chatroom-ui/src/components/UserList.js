import React from "react";

function UserList({ users }) {
  return (
    <div className="w-64 flex flex-col bg-white shadow relative">
      {/* Top bar */}
      <div
        className="px-4 py-3 backdrop-blur-md"
        style={{
          backgroundColor: "rgba(248, 248, 248, 0.7)",
        }}
      >
        <h1
          className="text-lg font-semibold"
          style={{
            fontFamily: "'Roboto', sans-serif",
            color: "black",
            fontSize: "20px",
          }}
        >
          Active Users
        </h1>
      </div>

      {/* User list */}
      <div className="flex-1 overflow-y-auto p-2">
        {users.map((user, index) => (
          <div key={index} className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <div
                className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-sm font-bold text-gray-700 mr-2"
                style={{ fontFamily: "'Roboto', sans-serif" }}
              >
                {user[0]}
              </div>
              <span
                className="font-bold"
                style={{ fontFamily: "'Roboto', sans-serif" }}
              >
                {user}
              </span>
            </div>
            <div className="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
          </div>
        ))}
      </div>
    </div>
  );
}


export default UserList;
