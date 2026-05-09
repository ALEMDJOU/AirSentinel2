"use client";

import { useEffect, useState } from "react";
import { HeartPulse, Baby, User, UserCog, ArrowRight, Loader2, ArrowLeft, MapPin, ChevronDown } from "lucide-react";
import mapService from "@/services/mapService";
import { useVille } from "@/context/VilleContext";
import { useLanguage } from "@/context/LanguageContext";
import { useRouter } from "next/navigation";

export default function SantePage() {
  const [loading, setLoading] = useState(true);
  const [villes, setVilles] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const { ville, selectVille } = useVille();
  const { t } = useLanguage();
  const router = useRouter();

  useEffect(() => {
    const fetchVilles = async () => {
      try {
        const points = await mapService.getMapPoints();
        const sortedVilles = points.map(p => p.city).sort((a, b) => a.localeCompare(b, 'fr'));
        setVilles(sortedVilles);
      } catch (err) {
        console.error("Erreur chargement villes:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchVilles();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-[#ef4444] animate-spin" />
      </div>
    );
  }

  const profiles = [
    {
      title: t('health_prof_children'),
      subtitle: t('health_desc_children'),
      icon: "👶",
      href: "/dashboard/sante/enfants",
      color: "bg-blue-500/20 border-blue-500/30 hover:border-blue-500/60",
      textColor: "text-blue-400"
    },
    {
      title: t('health_prof_adults'),
      subtitle: t('health_desc_adults'),
      icon: "🧑",
      href: "/dashboard/sante/adultes",
      color: "bg-green-500/20 border-green-500/30 hover:border-green-500/60",
      textColor: "text-green-400"
    },
    {
      title: t('health_prof_seniors'),
      subtitle: t('health_desc_seniors'),
      icon: "👴",
      href: "/dashboard/sante/personnes-agees",
      color: "bg-purple-500/20 border-purple-500/30 hover:border-purple-500/60",
      textColor: "text-purple-400"
    },
    {
      title: t('health_prof_asthma'),
      subtitle: t('health_desc_asthma'),
      icon: "🫁",
      href: "/dashboard/sante/asmatiques",
      color: "bg-red-500/20 border-red-500/30 hover:border-red-500/60",
      textColor: "text-red-400"
    }
  ];

  return (
    <main className="p-6 pb-24 max-w-5xl mx-auto animate-in fade-in duration-700">
      <header className="mb-10">
        <button
          onClick={() => router.push("/dashboard")}
          className="group flex items-center gap-3 px-5 py-2.5 bg-slate-900/60 backdrop-blur-md border border-white/20 rounded-2xl text-white hover:border-[#ef4444]/50 hover:bg-[#ef4444]/5 transition-all active:scale-95 shadow-lg mb-8"
        >
          <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform text-[#ef4444]" />
          <span className="font-black text-[11px] uppercase tracking-widest">{t('health_dash_link')}</span>
        </button>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 className="text-4xl font-black text-[#e0f2fe] mb-2 tracking-tight flex items-center gap-3">
              {t('health_title_1')}<span className="text-[#ef4444]">{t('health_title_2')}</span> <HeartPulse className="text-[#ef4444]" size={32} />
            </h1>
            <p className="text-[#e0f2fe]/50 text-sm font-medium italic">
              {ville ? t('health_sub_city_selected') : t('health_sub_no_city')}
            </p>
          </div>

          {ville && (
            <button
              onClick={() => selectVille("")}
              className="px-6 py-3 bg-[#00d4b1] text-white font-black uppercase tracking-tighter text-xs rounded-2xl shadow-[0_4px_20px_rgba(0,212,177,0.4)] hover:bg-[#00b89c] hover:scale-105 transition-all active:scale-95 flex items-center gap-2 shrink-0 border border-white/20"
            >
              <MapPin size={16} fill="white" />
              {t('health_change_city')} ({ville})
            </button>
          )}
        </div>
      </header>

      {!ville ? (
        <div className="glass-card p-10 flex flex-col items-center justify-center min-h-[400px] border-2 border-white/5 animate-in slide-in-from-bottom-5 duration-500">
          <div className="w-24 h-24 rounded-full bg-[#00d4b1]/10 flex items-center justify-center mb-8 relative">
            <div className="absolute inset-0 bg-[#00d4b1]/20 rounded-full blur-xl animate-pulse" />
            <MapPin className="text-[#00d4b1] relative z-10" size={48} />
          </div>
          
          <h2 className="text-3xl font-black text-white mb-4 text-center">{t('health_where_are_you')}</h2>
          <p className="text-gray-400 text-center mb-10 max-w-md text-base leading-relaxed">
            {t('health_where_desc')}
          </p>

          <div className="relative w-full max-w-md">
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="w-full flex items-center justify-between px-8 py-6 bg-[#00d4b1]/10 border-2 border-[#00d4b1]/50 rounded-[2rem] text-white hover:bg-[#00d4b1]/20 transition-all shadow-[0_0_30px_rgba(0,212,177,0.15)] group"
            >
              <div className="flex items-center gap-5">
                <div className="w-12 h-12 rounded-2xl bg-[#00d4b1] flex items-center justify-center text-white shadow-xl scale-110">
                  <MapPin size={24} fill="white" />
                </div>
                <span className="font-bold text-xl">{t('health_select_city')}</span>
              </div>
              <ChevronDown size={28} className={`text-[#00d4b1] transition-transform duration-500 ease-in-out ${showDropdown ? 'rotate-180' : ''}`} />
            </button>

            {showDropdown && (
              <div className="absolute top-full left-0 right-0 mt-4 bg-slate-900/95 backdrop-blur-2xl border border-white/10 rounded-[2rem] shadow-2xl overflow-hidden max-h-[350px] overflow-y-auto z-50 animate-in fade-in slide-in-from-top-4 duration-300">
                {villes.map((v) => (
                  <button
                    key={v}
                    onClick={() => { selectVille(v); setShowDropdown(false); }}
                    className="w-full text-left px-8 py-4 hover:bg-[#00d4b1]/20 text-white font-bold text-lg transition-all border-b border-white/5 last:border-0 hover:pl-10"
                  >
                    {v}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 animate-in slide-in-from-bottom-5 duration-700">
            {profiles.map((profile, idx) => (
              <button
                key={idx}
                onClick={() => router.push(profile.href)}
                className={`glass-card p-8 flex flex-col items-center text-center gap-4 border-2 transition-all duration-300 hover:scale-[1.02] ${profile.color}`}
              >
                <div className="text-6xl">{profile.icon}</div>
                <div>
                  <h3 className="text-xl font-black text-white mb-2">{profile.title}</h3>
                  <p className="text-sm text-gray-400">{profile.subtitle}</p>
                </div>
                <div className={`mt-2 flex items-center gap-2 ${profile.textColor}`}>
                  <span className="text-sm font-bold">{t('health_view_tips')}</span>
                  <ArrowRight size={16} />
                </div>
              </button>
            ))}
          </div>

          <div className="mt-12 p-6 bg-blue-500/5 rounded-3xl border border-blue-500/10 flex items-center gap-6 animate-in fade-in duration-1000">
            <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-400 shrink-0">
                <span className="text-xl font-bold">i</span>
            </div>
            <p className="text-xs text-gray-400 leading-relaxed font-medium">
               {t('health_ai_note')}
            </p>
          </div>
        </>
      )}

      <div className="h-[120px] sm:hidden" />
    </main>
  );
}
