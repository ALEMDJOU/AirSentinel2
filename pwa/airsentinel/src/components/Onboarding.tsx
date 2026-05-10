"use client";

import { useState, useEffect } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { useVille } from "@/context/VilleContext";
import { Bell, ChevronRight, Wind, ShieldCheck, CheckCircle } from "lucide-react";
import Image from "next/image";

export default function Onboarding() {
  const { t } = useLanguage();
  const { ville } = useVille();
  const [step, setStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const completed = localStorage.getItem("onboarding_completed");
    if (!completed) {
      setIsVisible(true);
    }
  }, []);

  // Automatiquement passer de l'étape 2 à 3 (Labor Illusion)
  useEffect(() => {
    if (step === 2) {
      const timer = setTimeout(() => nextStep(), 4000);
      return () => clearTimeout(timer);
    }
  }, [step]);

  if (!isVisible) return null;

  const nextStep = () => setStep((s) => s + 1);
  
  const handleFinish = () => {
    localStorage.setItem("onboarding_completed", "true");
    setIsVisible(false);
  };

  const skipOnboarding = () => {
    localStorage.setItem("onboarding_completed", "true");
    setIsVisible(false);
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-[#020c18]/80 backdrop-blur-md p-4 sm:p-6 transition-all duration-700">
      
      <div className="relative w-full max-w-lg bg-[#020c18] rounded-[40px] overflow-hidden shadow-[0_0_80px_rgba(0,0,0,0.5)] border border-white/10 flex flex-col min-h-[550px] animate-in fade-in zoom-in duration-700">
        
        {/* Background Image restricted to component */}
        <div className="absolute inset-0 z-0">
          <Image 
            src="/joel4.webp" 
            alt="Onboarding Background" 
            fill 
            className="object-cover opacity-60 scale-105 animate-slow-zoom"
            priority
          />
          {/* Internal Gradient Overlay for Legibility */}
          <div className="absolute inset-0 bg-gradient-to-t from-[#020c18] via-[#020c18]/80 to-[#020c18]/60" />
        </div>

        {/* Animated Accents inside the card */}
        <div className="absolute top-[-20px] right-[-20px] w-48 h-48 bg-[#00d4b1]/20 blur-[80px] pointer-events-none" />
        <div className="absolute bottom-[-20px] left-[-20px] w-48 h-48 bg-[#0ea5e9]/20 blur-[80px] pointer-events-none" />

        {/* Header / Skip */}
        {step < 3 && (
          <div className="flex justify-between items-center p-8 pb-0 z-10">
            <div className="flex gap-2">
              {[0, 1, 2, 3].map((i) => (
                <div 
                  key={i} 
                  className={`h-1.5 rounded-full transition-all duration-700 ${
                    i === step ? "w-10 bg-[#00d4b1]" : i < step ? "w-5 bg-[#00d4b1]/40" : "w-5 bg-white/10"
                  }`} 
                />
              ))}
            </div>
            <button 
              onClick={skipOnboarding}
              className="text-[11px] font-black uppercase tracking-[0.2em] text-white/40 hover:text-white transition-all hover:bg-white/5 py-2 px-4 rounded-full"
            >
              {t('onboarding_skip')}
            </button>
          </div>
        )}

        <div className="flex-1 flex flex-col p-8 sm:p-12 z-10 justify-center">
          
          {/* STEP 0: WELCOME */}
          {step === 0 && (
            <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in slide-in-from-bottom-8 duration-700">
              <div className="w-24 h-24 rounded-[30px] bg-gradient-to-br from-[#00d4b1]/20 to-[#00d4b1]/5 flex items-center justify-center mb-8 shadow-[0_0_40px_rgba(0,212,177,0.3)] border border-[#00d4b1]/20 animate-float">
                <Wind className="w-12 h-12 text-[#00d4b1]" />
              </div>
              <h1 className="text-3xl sm:text-4xl font-black text-white leading-tight mb-4 tracking-tight">
                {t('onboarding_welcome_title')}
              </h1>
              <p className="text-gray-200 text-lg font-medium leading-relaxed max-w-[300px]">
                {t('onboarding_welcome_desc')}
              </p>
              <button 
                onClick={nextStep}
                className="mt-10 btn-primary w-full group py-5 rounded-2xl text-lg shadow-[0_15px_30px_rgba(0,212,177,0.3)]"
              >
                <span className="flex items-center justify-center gap-3">
                  {t('onboarding_cta_start')}
                  <ChevronRight size={22} className="group-hover:translate-x-1.5 transition-transform" />
                </span>
              </button>
            </div>
          )}

          {/* STEP 1: NOTIFICATIONS */}
          {step === 1 && (
            <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in slide-in-from-right-12 duration-700">
              <div className="w-24 h-24 rounded-full bg-[#0ea5e9]/20 flex items-center justify-center mb-8 relative border border-[#0ea5e9]/30">
                <Bell className="w-12 h-12 text-[#0ea5e9] animate-ring" />
                <div className="absolute -top-1 -right-1 w-7 h-7 bg-red-500 rounded-full border-4 border-[#020c18] flex items-center justify-center">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                </div>
              </div>
              <h2 className="text-3xl font-black text-white mb-4 leading-tight">
                {t('onboarding_notif_title')}
              </h2>
              <p className="text-gray-200 text-lg font-medium leading-relaxed max-w-[280px] mb-10">
                {t('onboarding_notif_desc')}
              </p>
              
              <div className="w-full space-y-4">
                <button 
                  onClick={nextStep}
                  className="btn-primary w-full py-5 rounded-2xl text-lg shadow-[0_15px_40px_rgba(14,165,233,0.3)] bg-gradient-to-r from-[#0ea5e9] to-[#3b82f6]"
                >
                  {t('onboarding_cta_next')}
                </button>
                <button 
                  onClick={nextStep}
                  className="w-full py-2 text-white/40 font-bold hover:text-white transition-colors tracking-widest text-[10px] uppercase"
                >
                  {t('onboarding_skip')}
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: LABOR ILLUSION / LOADING */}
          {step === 2 && (
            <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in duration-700">
              <div className="relative w-28 h-28 mb-10">
                <div className="absolute inset-0 rounded-full border-[6px] border-white/5" />
                <div className="absolute inset-0 rounded-full border-[6px] border-t-[#00d4b1] animate-spin-slow" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <ShieldCheck className="w-12 h-12 text-[#00d4b1] animate-pulse" />
                </div>
              </div>
              <h2 className="text-3xl font-black text-white mb-3">
                {t('onboarding_final_title')}
              </h2>
              <p className="text-[#00d4b1] text-sm font-black uppercase tracking-[0.3em] animate-pulse">
                {t('onboarding_final_desc')}
              </p>
              
              <div className="mt-10 space-y-2">
                <div className="flex items-center gap-3 text-white/40 text-[10px] font-bold uppercase tracking-widest bg-white/5 px-4 py-2 rounded-lg">
                  <div className="w-1 h-1 rounded-full bg-[#00d4b1] animate-ping" />
                  {t('onboarding_alert_config').replace('{}', ville)}
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: AHA MOMENT */}
          {step === 3 && (
            <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in zoom-in duration-1000">
              <div className="w-24 h-24 rounded-full bg-[#00d4b1] flex items-center justify-center mb-8 shadow-[0_0_60px_rgba(0,212,177,0.6)] border-4 border-white/20">
                <CheckCircle className="w-12 h-12 text-[#020c18]" />
              </div>
              <h2 className="text-4xl font-black text-white mb-4 tracking-tight">
                {t('onboarding_aha_title')}
              </h2>
              <p className="text-white text-lg font-bold leading-relaxed max-w-[320px] mb-12 bg-white/10 py-5 px-6 rounded-3xl backdrop-blur-xl border border-white/10">
                {t('onboarding_aha_desc').replace('{}', ville || t('nav_user_placeholder'))}
              </p>
              <button 
                onClick={handleFinish}
                className="btn-primary w-full scale-105 py-5 rounded-2xl text-xl font-black shadow-[0_20px_50px_rgba(0,212,177,0.4)]"
              >
                {t('onboarding_cta_finish')}
              </button>
            </div>
          )}

        </div>
      </div>
      
      <style jsx>{`
        .animate-float {
          animation: float 6s ease-in-out infinite;
        }
        .animate-slow-zoom {
          animation: slowZoom 40s linear infinite alternate;
        }
        .animate-spin-slow {
          animation: spin 3s linear infinite;
        }
        .animate-ring {
          animation: ring 2s ease-in-out infinite;
        }
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-15px); }
        }
        @keyframes slowZoom {
          from { transform: scale(1.05) translate(0, 0); }
          to { transform: scale(1.3) translate(-2%, -2%); }
        }
        @keyframes ring {
          0%, 100% { transform: rotate(0); }
          10%, 30%, 50%, 70%, 90% { transform: rotate(-10deg); }
          20%, 40%, 60%, 80% { transform: rotate(10deg); }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
