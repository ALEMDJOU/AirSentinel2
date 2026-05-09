import React from "react";
import { toast, Toast } from "react-hot-toast";
import { CheckCircle2, AlertCircle, Info, X, Loader2 } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface CustomToastProps {
  t: Toast;
  message: string;
  type: "success" | "error" | "info" | "loading";
}

const CustomToast: React.FC<CustomToastProps> = ({ t, message, type }) => {
  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
    error: <AlertCircle className="w-5 h-5 text-rose-400" />,
    info: <Info className="w-5 h-5 text-sky-400" />,
    loading: <Loader2 className="w-5 h-5 text-teal-400 animate-spin" />,
  };

  const bgStyles = {
    success: "border-emerald-500/20 shadow-emerald-500/10",
    error: "border-rose-500/20 shadow-rose-500/10",
    info: "border-sky-500/20 shadow-sky-500/10",
    loading: "border-teal-500/20 shadow-teal-500/10",
  };

  return (
    <div
      className={cn(
        "flex items-center gap-3 min-w-[300px] max-w-md p-4 rounded-2xl border backdrop-blur-xl bg-slate-900/80 text-white shadow-2xl transition-all duration-300",
        bgStyles[type],
        t.visible ? "animate-fade-in" : "animate-fade-out"
      )}
    >
      <div className="flex-shrink-0">{icons[type]}</div>
      <div className="flex-1 text-[14px] font-medium leading-tight">
        {message}
      </div>
      <button
        onClick={() => toast.dismiss(t.id)}
        className="flex-shrink-0 p-1 hover:bg-white/10 rounded-full transition-colors"
      >
        <X className="w-4 h-4 text-gray-400" />
      </button>
    </div>
  );
};

export default CustomToast;
