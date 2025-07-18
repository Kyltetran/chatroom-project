import React, { useState, useRef, useEffect } from "react";

const emojiShortcuts = {
    "#smile ": "😃",
    "#cry ": "😢",
    "#sad ": "😞",
    "#angry ": "😡",
    "#eww ": "🤢",
    "#haha ": "😂",
};

function InputArea({ onSend }) {
    const [text, setText] = useState("");
    const [showEmoji, setShowEmoji] = useState(false);
    const emojiPickerRef = useRef();
    const inputRef = useRef();

    // Close emoji picker when clicking outside
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (emojiPickerRef.current && !emojiPickerRef.current.contains(e.target)) {
                setShowEmoji(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSend = () => {
        if (text.trim() !== "") {
            onSend(text.trim());
            setText("");
            inputRef.current?.focus(); // Return focus to input after sending
        }
    };

    // try handling private message
    /*const handleSend = (text) => {
        // We just forward raw text (e.g., "/w Bob Hello!") to Python client
        ws.send(JSON.stringify({ type: "message", text, sender: myName }));
      };*/
      

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            onSend(`📎 Sent file: ${file.name}`);
        }
    };

    const handleInputChange = (e) => {
        let newText = e.target.value;
        Object.entries(emojiShortcuts).forEach(([shortcut, emoji]) => {
            const regex = new RegExp(`${shortcut}(?=\\s|$)`, "g");
            newText = newText.replace(regex, emoji);
        });
        setText(newText);
    };

    return (
        <div className="relative flex items-center p-2 bg-white border-t">
            {/* Emoji Picker */}
            {showEmoji && (
                <div
                    ref={emojiPickerRef}
                    className="absolute bottom-14 left-12 p-4 backdrop-blur-lg"
                    style={{
                        backgroundColor: "rgba(246, 246, 246, 0.6)",
                        borderRadius: "20.6px",
                        boxShadow: `
              0px 0px 2.15px rgba(0, 0, 0, 0.6),
              0px 0px 4.29px rgba(0, 0, 0, 0.05),
              0px 81.58px 193.2px rgba(0, 0, 0, 0.25)
            `,
                    }}
                >
                    <div className="grid grid-cols-8 gap-2">
                        {["😀","😃","😄","😁","😆","😅","😂","🤣","🥲","😊","😇","🙂","🙃","😉","😌","😍","😘","😗","😙","😚","😋","😛","😝","😜","🤪","🤨","🧐","🤓","😎","🥸","🤩","🥳","😏","😒","😞","😔","😟","😕","🙁","☹️","😣","😖","😫","😩","🥺","😢","😭","😤","😠","😡","🤬","🤯","😳","🥵","🥶","😱","😨","😰","😥","😓","🤗","🤔","🤭","🤫","🤥","😶","😐","😑","😬","🙄","😯","😦","😧","😮","😲","🥱","😴","🤤","😪","😵","🤐","🥴","🤢","🤮","🤧","😷","🤒","🤕"].map((emoji) => (
                            <button
                                key={emoji}
                                className="text-xl"
                                onClick={() => setText((prev) => prev + emoji)}
                            >
                                {emoji}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* File icon */}
            <label className="cursor-pointer mr-2">
                📎
                <input
                    type="file"
                    className="hidden"
                    onChange={handleFileSelect}
                />
            </label>

            {/* Emoji icon */}
            <button
                className="mr-2"
                onClick={() => setShowEmoji(!showEmoji)}
            >
                😊
            </button>

            {/* Input field */}
            <input
                ref={inputRef}
                className="flex-1 px-4 py-2 mr-2"
                style={{
                    backgroundColor: "rgba(205, 205, 205, 0.28)",
                    borderRadius: "45.5px",
                    fontFamily: "'Roboto', sans-serif",
                }}
                placeholder="@Username for private messages, # for emojis"
                value={text}
                onChange={handleInputChange}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />

            {/* Send button */}
            <button
                className="px-5 py-2 text-white"
                style={{
                    backgroundColor: "#0E6E3B",
                    borderRadius: "80px",
                    fontFamily: "'Roboto', sans-serif",
                }}
                onClick={handleSend}
            >
                Send
            </button>
        </div>
    );
}

export default InputArea;
