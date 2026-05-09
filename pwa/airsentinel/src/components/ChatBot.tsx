"use client";

import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import {
  X,
  Send,
  Loader2,
  RotateCcw,
  Sparkles,
  Zap,
} from "lucide-react";
import apiClient from "@/services/apiClient";
import { useLanguage } from "@/context/LanguageContext";

// ──────────────────────────────────────────────
// Types
// ──────────────────────────────────────────────
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  error?: boolean;
}

interface Pos {
  x: number;
  y: number;
}

// ──────────────────────────────────────────────
// Config & Helpers
// ──────────────────────────────────────────────
// We will move QUICK_SUGGESTIONS inside the component or use a hook to get translated versions

function parseMarkdown(text: string): string {
  if (!text) return "";
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`(.*?)`/g, '<code class="bg-white/10 px-1 rounded text-[11px] font-mono">$1</code>')
    .replace(/\n/g, "<br />");
}

export default function ChatBot() {
  const { t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  
  const QUICK_SUGGESTIONS = useMemo(() => [
    t('sug_irs'),
    t('sug_harmattan'),
    t('sug_alerts'),
  ], [t]);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: t('bot_welcome'),
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  // Mettre à jour le message de bienvenue si la langue change
  useEffect(() => {
    setMessages(prev => prev.map(msg => 
      msg.id === "welcome" ? { ...msg, content: t('bot_welcome') } : msg
    ));
  }, [t]);

  // Positions & Dragging
  const [windowPos, setWindowPos] = useState<Pos | null>(null);
  const [fabPos, setFabPos] = useState<Pos>({ x: -1, y: -1 });
  const [isDraggingWin, setIsDraggingWin] = useState(false);
  const [isDraggingFab, setIsDraggingFab] = useState(false);
  const [hasMovedFab, setHasMovedFab] = useState(false);

  const dragStartRef = useRef<{ mx: number; my: number; x: number; y: number } | null>(null);
  const windowRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // ──────────────────────────────────────────────
  // Logique de Défilement
  // ──────────────────────────────────────────────
  const scrollToBottom = useCallback((smooth = true) => {
    messagesEndRef.current?.scrollIntoView({ behavior: smooth ? "smooth" : "auto" });
  }, []);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        scrollToBottom(false);
        inputRef.current?.focus();
      }, 100);
    }
  }, [isOpen, scrollToBottom]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  // ──────────────────────────────────────────────
  // Gestion du Drag & Drop
  // ──────────────────────────────────────────────
  const onWinDragStart = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('button')) return;
    setIsDraggingWin(true);
    const rect = windowRef.current?.getBoundingClientRect();
    if (!rect) return;
    dragStartRef.current = { mx: e.clientX, my: e.clientY, x: rect.left, y: rect.top };
    e.preventDefault();
  };

  const onFabDragStart = (e: React.MouseEvent) => {
    setIsDraggingFab(true);
    setHasMovedFab(false);
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    dragStartRef.current = { mx: e.clientX, my: e.clientY, x: rect.left, y: rect.top };
    e.preventDefault();
  };

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!dragStartRef.current) return;
      const dx = e.clientX - dragStartRef.current.mx;
      const dy = e.clientY - dragStartRef.current.my;

      if (isDraggingWin) {
        const winW = 360;
        const winH = 540;
        setWindowPos({
          x: Math.max(8, Math.min(window.innerWidth - winW - 8, dragStartRef.current.x + dx)),
          y: Math.max(8, Math.min(window.innerHeight - winH - 8, dragStartRef.current.y + dy)),
        });
      } else if (isDraggingFab) {
        if (Math.abs(dx) > 5 || Math.abs(dy) > 5) setHasMovedFab(true);
        setFabPos({
          x: Math.max(8, Math.min(window.innerWidth - 64, dragStartRef.current.x + dx)),
          y: Math.max(8, Math.min(window.innerHeight - 64, dragStartRef.current.y + dy)),
        });
      }
    };

    const onUp = () => {
      setIsDraggingWin(false);
      setIsDraggingFab(false);
      dragStartRef.current = null;
    };

    if (isDraggingWin || isDraggingFab) {
      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    }
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [isDraggingWin, isDraggingFab]);

  // ──────────────────────────────────────────────
  // Actions
  // ──────────────────────────────────────────────
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  const sendMessage = async (text?: string) => {
    const content = (text || input).trim();
    if (!content || isLoading) return;

    const userMessage: Message = { 
        id: `user-${Date.now()}`, 
        role: "user", 
        content, 
        timestamp: new Date() 
    };

    setMessages((p) => [...p, userMessage]);
    setInput("");
    if (inputRef.current) inputRef.current.style.height = "auto";
    setIsLoading(true);

    try {
      const history = messages
        .filter(m => !m.error && m.id !== "welcome")
        .slice(-6)
        .map(m => ({ role: m.role, content: m.content }));

      const res = await apiClient.post("/chat/ask", { message: content, history });
      
      setMessages((p) => [...p, { 
        id: `bot-${Date.now()}`, 
        role: "assistant", 
        content: res.data.reply, 
        timestamp: new Date() 
      }]);
    } catch (err) {
      setMessages((p) => [...p, { 
        id: `err-${Date.now()}`, 
        role: "assistant", 
        content: t('bot_error'), 
        timestamp: new Date(), 
        error: true 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetChat = () => {
    setMessages([{
        id: "welcome",
        role: "assistant",
        content: t('bot_reset_msg'),
        timestamp: new Date(),
    }]);
  };

  const winStyle = useMemo<React.CSSProperties>(() => (
    windowPos ? { left: windowPos.x, top: windowPos.y } : { bottom: "100px", right: "24px" }
  ), [windowPos]);

  const fStyle = useMemo<React.CSSProperties>(() => (
    fabPos.x !== -1 ? { left: fabPos.x, top: fabPos.y } : { bottom: "24px", right: "24px" }
  ), [fabPos]);

  return (
    <>
      <style>{`
        .chat-glass { 
            background: #0f172a; 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            box-shadow: 0 20px 50px -12px rgba(0,0,0,0.6); 
        }
        .sentinel-scroll::-webkit-scrollbar { width: 4px; }
        .sentinel-scroll::-webkit-scrollbar-thumb { 
            background: rgba(16, 185, 129, 0.2); 
            border-radius: 10px; 
        }
        .sentinel-scroll::-webkit-scrollbar-thumb:hover { background: rgba(16, 185, 129, 0.4); }
        @keyframes message-in {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-message { animation: message-in 0.3s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
      `}</style>

      {isOpen && (
        <div
          ref={windowRef}
          style={{ ...winStyle, position: "fixed", width: "360px", height: "540px", zIndex: 1000 }}
          className="chat-glass flex flex-col rounded-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-300"
        >
          {/* Header */}
          <div 
            onMouseDown={onWinDragStart} 
            className="flex-shrink-0 cursor-grab active:cursor-grabbing bg-slate-900/40 backdrop-blur-xl border-b border-white/5 p-4 flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                    <Zap size={20} className="text-white fill-white" />
                </div>
                <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 border-2 border-slate-900 rounded-full" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight">SentinelIA</h3>
                <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                    <span className="text-[10px] text-slate-400 font-medium uppercase tracking-widest">{t('bot_online')}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1">
                <button onClick={resetChat} title={t('bot_reset')} className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all">
                    <RotateCcw size={14} />
                </button>
                <button onClick={() => setIsOpen(false)} className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-all">
                    <X size={16} />
                </button>
            </div>
          </div>

          {/* Messages Body */}
          <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#0b1120] sentinel-scroll relative">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"} animate-message`}>
                <div className={`max-w-[85%] p-3.5 rounded-2xl text-[13px] leading-relaxed shadow-sm ${
                    msg.role === "user" 
                    ? "bg-emerald-500 text-white font-medium rounded-tr-none shadow-emerald-500/10" 
                    : "bg-slate-800/60 text-slate-200 border border-white/5 rounded-tl-none"
                }`}>
                  <div dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }} />
                </div>
                <span className="text-[9px] text-slate-500 mt-1.5 px-1 font-medium opacity-60">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}

            {messages.length === 1 && !isLoading && (
                <div className="pt-2 flex flex-wrap gap-2 animate-message">
                    {QUICK_SUGGESTIONS.map((s) => (
                        <button 
                            key={s} 
                            onClick={() => sendMessage(s)}
                            className="text-[11px] bg-slate-800/30 hover:bg-emerald-500/10 border border-white/5 hover:border-emerald-500/30 text-slate-400 hover:text-emerald-400 px-3.5 py-1.5 rounded-full transition-all flex items-center gap-2"
                        >
                            <Sparkles size={10} />
                            {s}
                        </button>
                    ))}
                </div>
            )}

            {isLoading && (
              <div className="flex justify-start animate-pulse">
                <div className="bg-slate-800/40 border border-white/5 p-3 rounded-2xl rounded-tl-none flex gap-1.5 items-center">
                    <span className="w-1.5 h-1.5 bg-emerald-500/60 rounded-full animate-bounce" />
                    <span className="w-1.5 h-1.5 bg-emerald-500/60 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <span className="w-1.5 h-1.5 bg-emerald-500/60 rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} className="h-2" />
          </div>

          {/* Footer Input */}
          <div className="flex-shrink-0 bg-slate-900/50 backdrop-blur-md p-3 border-t border-white/5">
            <div className="flex items-end gap-2 bg-slate-800/40 border border-white/5 rounded-xl p-2 focus-within:border-emerald-500/30 transition-all duration-300">
              <textarea 
                ref={inputRef} 
                rows={1} 
                value={input} 
                onChange={handleInputChange} 
                onKeyDown={(e) => { 
                    if(e.key === "Enter" && !e.shiftKey) { 
                        e.preventDefault(); 
                        sendMessage(); 
                    } 
                }} 
                placeholder={t('bot_placeholder')} 
                className="flex-1 bg-transparent border-none focus:ring-0 text-[13px] text-white py-1.5 px-2 resize-none max-h-32 sentinel-scroll placeholder:text-slate-500" 
              />
              <button 
                onClick={() => sendMessage()} 
                disabled={!input.trim() || isLoading} 
                className="flex-shrink-0 w-9 h-9 flex items-center justify-center bg-emerald-500 text-white rounded-lg disabled:opacity-20 disabled:grayscale transition-all hover:bg-emerald-400 active:scale-95 shadow-lg shadow-emerald-500/20"
              >
                {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
              </button>
            </div>
            <p className="text-[9px] text-center text-slate-600 mt-2.5 font-medium">
                {t('bot_mistakes')}
            </p>
          </div>
        </div>
      )}

      {/* FAB Button */}
      <button
        onMouseDown={onFabDragStart}
        onClick={() => !hasMovedFab && setIsOpen(!isOpen)}
        style={{ ...fStyle, position: "fixed", zIndex: 1001 }}
        className={`w-14 h-14 rounded-2xl flex items-center justify-center shadow-2xl transition-all duration-500 cursor-grab active:cursor-grabbing hover:scale-105 active:scale-95 group ${
          isOpen 
          ? "bg-slate-800 text-white rotate-180 border border-white/10" 
          : "bg-gradient-to-br from-emerald-400 to-teal-600 text-white shadow-emerald-500/30"
        }`}
      >
        {isOpen ? (
          <X size={24} className="transition-transform duration-500" />
        ) : (
          <div className="relative">
            <Zap size={28} className="fill-white transition-transform group-hover:scale-110" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-white rounded-full animate-ping opacity-20" />
          </div>
        )}
      </button>
    </>
  );
}