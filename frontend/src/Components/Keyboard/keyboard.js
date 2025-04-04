import React from "react";
import "./keyboard.css"; // Import the CSS file

const VirtualKeyboard = ({ onKeyPress }) => {
  // keyboard layout
  const rows = [
    ["~", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
    ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
    ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
    ["Ctrl", "Alt", "Space", "Alt", "Ctrl"]
  ];

  return (
    <div className="keyboard">
      {rows.map((row, rowIndex) => (
        <div key={rowIndex} className="row">
          {row.map((key, keyIndex) => (
            <div
              key={`${rowIndex}-${keyIndex}`}
              className="key"
              onMouseDown={(e) => {
                e.preventDefault(); // ensures it stays in textbox to type manually or virtually
                onKeyPress(key);
              }}
            >
              {key}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};


export default VirtualKeyboard;