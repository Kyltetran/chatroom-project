import React, { useEffect, useRef } from "react";
import dayjs from "dayjs";

function ChatArea({ messages }) {
    const scrollRef = useRef();

    useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    return (
        <div
            className="flex-1 p-4 overflow-y-auto bg-white"
            style={{ fontFamily: "'Roboto', sans-serif" }}
        >
            {messages.map((msg, i) => {
                const isMe = msg.user === "You";
                const nextMsg = messages[i + 1];
                const showTimestamp = !nextMsg || nextMsg.user !== msg.user || nextMsg.system;
                const isFirstInGroup = !i || messages[i - 1].user !== msg.user;

                // System message
                if (msg.system) {
                    return (
                        <div key={msg.id} className="flex justify-center my-4">
                            <div
                                className="rounded-full px-4 py-2 max-w-[80%] text-center"
                                style={{
                                    backgroundColor: "rgba(217, 241, 219, 0.5)",
                                    fontFamily: "'Roboto', sans-serif",
                                }}
                            >
                                <span
                                    style={{
                                        color: "#696969",
                                        fontSize: "16px",
                                    }}
                                >
                                    {dayjs(msg.timestamp).format("ddd DD MMM HH:mm:ss")}{" "}
                                </span>
                                <span
                                    style={{
                                        color: "black",
                                        fontWeight: "bold",
                                        fontSize: "16px",
                                    }}
                                >
                                    {msg.text}
                                </span>
                            </div>
                        </div>
                    );
                }

                return (
                    <div
                        key={msg.id}
                        className={`flex flex-row items-start ${
                            isMe ? "justify-end" : "justify-start"
                        } ${isFirstInGroup ? "mt-3" : "mt-1"}`}
                    >
                        {/* Avatar */}
                        {!isMe && isFirstInGroup && (
                            <div className="mr-2">
                                <div
                                    className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-sm font-bold text-gray-700 shadow-sm"
                                >
                                    {msg.user[0]}
                                </div>
                            </div>
                        )}

                        <div
                            className={`flex flex-col ${
                                isMe ? "items-end" : "items-start"
                            } max-w-[70%]`}
                        >
                            {/* Sender name */}
                            {isFirstInGroup && !isMe && (
                                <div
                                    className="mb-1 ml-1"
                                    style={{
                                        fontWeight: "bold",
                                        fontSize: "16px",
                                        color: "black",
                                    }}
                                >
                                    {msg.user}
                                </div>
                            )}

                            {/* Message bubble */}
                            <div
                                className={`px-4 py-2 shadow-md transition-all duration-300 ease-in-out select-text`}
                                style={{
                                    backgroundColor: isMe
                                        ? "#0E6E3B"
                                        : "rgba(205, 205, 205, 0.43)",
                                    color: isMe ? "white" : "black",
                                    borderRadius:
                                        msg.text.length <= 60 ? "45.5px" : "20px",
                                    fontSize: "16px", // Smaller and modern
                                    lineHeight: "22px",
                                }}
                            >
                                {msg.text}
                            </div>

                            {/* Timestamp */}
                            {showTimestamp && (
                                <div
                                    className="mt-1 ml-1"
                                    style={{
                                        color: "#A2A2A2",
                                        fontWeight: 600,
                                        fontSize: "13px",
                                    }}
                                >
                                    {dayjs(msg.timestamp).format("ddd DD MMM HH:mm:ss")}
                                </div>
                            )}
                        </div>
                    </div>
                );
            })}
            <div ref={scrollRef}></div>
        </div>
    );
}

export default ChatArea;