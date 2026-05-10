"use client";

import { useState, useEffect } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { useVille } from "@/context/VilleContext";
import { Bell, ChevronRight, Wind, ShieldCheck, CheckCircle } from "lucide-react";

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
      const timer = setTimeout(() => nextStep(), 3000);
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
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-[#020c18]/95 backdrop-blur-xl p-4 sm:p-6 transition-all duration-500">
      <div className="relative w-full max-w-lg bg-white/5 border border-white/10 rounded-[32px] overflow-hidden shadow-2xl flex flex-col min-h-[500px]">
        
        {/* Background Blobs */}
        <div className="absolute top-[-100px] left-[-100px] w-64 h-64 bg-[#00d4b1]/10 blur-[80px] pointer-events-none" />
        <div className="absolute bottom-[-100px] right-[-100px] w-64 h-64 bg-[#0ea5e9]/10 blur-[80px] pointer-events-none" />

        {/* Header / Skip */}
        {step < 3 && (
          <div className="flex justify-between items-center p-6 pb-0 z-10">
            <div className="flex gap-1.5">
              {[0, 1, 2, 3].map((i) => (
                <div 
                  key={i} 
                  className={`h-1 rounded-full transition-all duration-500 ${
                    i === step ? "w-8 bg-[#00d4b1]" : i < step ? "w-4 bg-[#00d4b1]/30" : "w-4 bg-white/10"
                  }`} 
                />
              ))}
            </div>
            <button 
              onClick={skipOnboarding}
              className="text-[10px] font-black uppercase tracking-widest text-white/30 hover:text-white transition-colors"
            >
              {t('onboarding_skip')}
            </button>
          </div>
        )}

        <div className="flex-1 flex flex-col p-8 z-10">
          
          {/* STEP 0: WELCOME */}
          {step === 0 && (
            <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in zoom-in duration-500">
              <div className="w-24 h-24 rounded-3xl bg-[#00d4b1]/10 flex items-center justify-center mb-8 shadow-[0_0_40px_rgba(0,212,177,0.2)] animate-float">
                <Wind className="w-12 h-12 text-[#00d4b1]" />
              </div>
              <h1 className="text-3xl font-black text-white leading-tight mb-4">
                {t('onboarding_welcome_title')}
              </h1>
              <p className="text-gray-400 text-lg font-medium leading-relaxed max-w-[280px]">
                {t('onboarding_welcome_desc')}
              </p>
              <button 
                onClick={nextStep}
                className="mt-10 btn-primary w-full group"
              >
                <span className="flex items-center justify-center gap-2">
                  {t('onboarding_cta_start')}
                  <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </span>
              </button>
            </div>
          )}

          {/* STEP 1: NOTIFICATIONS */}
          {step === 1 && (
            <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in slide-in-from-right-8 duration-500">
              <div className="w-20 h-20 rounded-full bg-[#0ea5e9]/10 flex items-center justify-center mb-8 relative">
                <Bell className="w-10 h-10 text-[#0ea5e9] animate-bounce" />
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full border-4 border-[#020c18] flex items-center justify-center">
                  <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                </div>
              </div>
              <h2 className="text-2xl font-black text-white mb-4">
                {t('onboarding_notif_title')}
              </h2>
              <p className="text-gray-400 font-medium leading-relaxed max-w-[280px] mb-8">
                {t('onboarding_notif_desc')}
              </p>
              
              <div className="w-full space-y-3">
                <button 
                  onClick={nextStep}
                  className="btn-primary w-full shadow-[0_0_30px_rgba(14,165,233,0.3)]"
                >
                  {t('onboarding_cta_next')}
                </button>
                <button 
                  onClick={nextStep}
                  className="w-full py-4 text-gray-500 font-bold hover:text-white transition-colors"
                >
                  {t('onboarding_skip')}
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: LABOR ILLUSION / LOADING */}
          {step === 2 && (
            <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in duration-500">
              <div className="relative w-24 h-24 mb-8">
                <div className="absolute inset-0 rounded-full border-4 border-white/5" />
                <div className="absolute inset-0 rounded-full border-4 border-t-[#00d4b1] animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <ShieldCheck className="w-10 h-10 text-[#00d4b1]" />
                </div>
              </div>
              <h2 className="text-2xl font-black text-white mb-3">
                {t('onboarding_final_title')}
              </h2>
              <p className="text-[#00d4b1] text-xs font-black uppercase tracking-[0.2em] animate-pulse">
                {t('onboarding_final_desc')}
              </p>
            </div>
          )}

          {/* STEP 3: AHA MOMENT */}
          {step === 3 && (
            <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in zoom-in duration-700">
              <div className="w-24 h-24 rounded-full bg-[#00d4b1] flex items-center justify-center mb-8 shadow-[0_0_60px_rgba(0,212,177,0.5)]">
                <CheckCircle className="w-12 h-12 text-[#020c18]" />
              </div>
              <h2 className="text-4xl font-black text-white mb-4">
                {t('onboarding_aha_title')}
              </h2>
              <p className="text-gray-400 text-lg font-medium leading-relaxed max-w-[300px] mb-10">
                {t('onboarding_aha_desc').replace('{}', ville || '')}
              </p>
              <button 
                onClick={handleFinish}
                className="btn-primary w-full scale-110"
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
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
      `}</style>
    </div>
  );
}
