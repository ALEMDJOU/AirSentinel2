"use client";

import { useTheme } from "@/context/ThemeContext";
import { Sun, Moon } from "lucide-react";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative flex items-center justify-between w-14 h-7 rounded-full p-1 bg-[var(--bg-secondary)] border border-[var(--border-color)] shadow-inner cursor-pointer transition-all duration-500 hover:border-[var(--teal)]/50 group"
      aria-label="Toggle theme"
    >
      <div
        className={`absolute top-0.5 bottom-0.5 w-6 h-6 rounded-full flex items-center justify-center transition-all duration-500 transform ${
          theme === "dark" 
            ? "translate-x-6 bg-[#1e293b] shadow-[0_0_15px_rgba(30,41,59,0.5)]" 
            : "translate-x-0 bg-white shadow-[0_0_15px_rgba(255,255,255,0.8)]"
        }`}
      >
        {theme === "dark" ? (
          <Moon size={14} className="text-indigo-400 group-hover:rotate-12 transition-transform" />
        ) : (
          <Sun size={14} className="text-amber-500 group-hover:rotate-45 transition-transform" />
        )}
      </div>
      
      <div className="flex w-full justify-around items-center px-0.5 pointer-events-none">
         <Sun size={10} className={`${theme === 'light' ? 'opacity-0' : 'opacity-40'} text-amber-500 transition-opacity`} />
         <Moon size={10} className={`${theme === 'dark' ? 'opacity-0' : 'opacity-40'} text-indigo-400 transition-opacity`} />
      </div>
    </button>
  );
}
