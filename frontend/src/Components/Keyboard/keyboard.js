import React, { useEffect, useRef, useState } from "react";
import "./keyboard.css";

const VirtualKeyboard = ({ onKeyPress }) => {
  const keyboardRef = useRef(null);
  const containerRef = useRef(null);
  const [scale, setScale] = useState(1);

  // Add Wordle-style symbols for special keys
  const getKeySymbol = (key) => {
    switch (key) {
      case 'Backspace':
        return '←';
      case 'Space':
        return ' ';
      default:
        return key.toLowerCase();
    }
  };

  useEffect(() => {
    const calculateScale = () => {
      if (!keyboardRef.current || !containerRef.current) return;
      
      const container = containerRef.current.parentElement;
      const keyboard = keyboardRef.current;
      
      const containerWidth = container.clientWidth;
      const containerHeight = container.clientHeight;
      
      const keyboardWidth = keyboard.scrollWidth;
      const keyboardHeight = keyboard.scrollHeight;
      
      const widthScale = containerWidth / keyboardWidth;
      const heightScale = containerHeight / keyboardHeight;
      
      const newScale = Math.min(widthScale, heightScale, 1) * 0.95;
      
      setScale(newScale);
    };

    const resizeObserver = new ResizeObserver(calculateScale);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current.parentElement);
    }

    return () => resizeObserver.disconnect();
  }, []);

  const rows = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Backspace"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Enter"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["Ctrl", "Alt", "Space", "Alt", "Ctrl"]
  ];

  return (
    <div ref={containerRef} className="keyboard-wrapper">
      <div 
        ref={keyboardRef} 
        className="keyboard"
        style={{
          transform: `scale(${scale})`,
          transformOrigin: 'center center'
        }}
      >
        {rows.map((row, rowIndex) => (
          <div key={rowIndex} className="row">
            {row.map((key, keyIndex) => (
              <div
                key={`${rowIndex}-${keyIndex}`}
                className={`key`}
                onMouseDown={(e) => {
                  e.preventDefault();
                  onKeyPress(key.toLowerCase());
                }}
              >
                {getKeySymbol(key)}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default VirtualKeyboard;