"use client";

import { useState, useEffect } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { Globe } from "lucide-react";

export default function LanguageSwitcher() {
  const { lang, setLang } = useLanguage();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <button 
      onClick={() => setLang(lang === 'fr' ? 'en' : 'fr')}
      className="flex items-center gap-1.5 px-2 py-1 bg-white/5 border border-white/10 rounded-lg text-xs font-bold hover:bg-white/10 transition-colors z-50 text-white"
    >
      <Globe size={14} className="text-[#00d4b1]" />
      {lang.toUpperCase()}
    </button>
  );
}
