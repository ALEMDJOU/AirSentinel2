"use client";

import { useEffect, useState } from "react";
import { HeartPulse, ShieldCheck, Loader2, MapPin, ChevronDown, AlertTriangle } from "lucide-react";
import healthService, { ProfilRecommandation } from "@/services/healthService";
import mapService from "@/services/mapService";
import { useVille } from "@/context/VilleContext";
import { useLanguage } from "@/context/LanguageContext";
import HealthNav from "@/components/HealthNav";
import { useRouter } from "next/navigation";

export default function PersonnesAgeesPage() {
  const [recommendations, setRecommendations] = useState<ProfilRecommandation[]>([]);
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
      }
    };
    fetchVilles();
  }, []);

  useEffect(() => {
    if (!ville) {
      setLoading(false);
      return;
    }

    const fetchHealthData = async () => {
      setLoading(true);
      try {
        const data = await healthService.getRealRecommendations(ville);
        const ageeRec = data.find(r => r.profil.toLowerCase().includes("âgée") || r.profil.toLowerCase().includes("agee"));
        setRecommendations(ageeRec ? [ageeRec] : []);
      } catch (err) {
        console.error("Erreur chargement santé:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHealthData();
  }, [ville]);

  const handleSelectVille = (villeChoisie: string) => {
    selectVille(villeChoisie);
    setShowDropdown(false);
  };

  if (!ville) {
    return (
      <main className="p-6 pb-24 max-w-5xl mx-auto animate-in fade-in duration-700">
        <HealthNav currentPage="personnes-agees" />
        <header className="mb-10">
          <h1 className="text-4xl font-black text-[#e0f2fe] mb-2 tracking-tight flex items-center gap-3">
            {t('health_title_1')} <span className="text-purple-400">{t('health_prof_seniors')}</span> <span className="text-3xl">👴</span>
          </h1>
          <p className="text-[#e0f2fe]/50 text-sm font-medium italic">{t('health_desc_seniors')}</p>
        </header>

        <div className="glass-card p-10 flex flex-col items-center justify-center min-h-[400px]">
          <div className="w-20 h-20 rounded-full bg-[#00d4b1]/10 flex items-center justify-center mb-6">
            <MapPin className="text-[#00d4b1]" size={40} />
          </div>
          <h2 className="text-2xl font-black text-white mb-4 text-center">{t('health_city_choose')}</h2>
          <p className="text-gray-400 text-center mb-8 max-w-md">
            {t('health_req_city').replace('{}', t('health_prof_seniors').toLowerCase())}
          </p>

          <div className="relative w-full max-w-md">
            <button
              onClick={() => setShowDropdown(!showDropdown)}
              className="w-full flex items-center justify-between px-6 py-5 bg-[#00d4b1]/10 border-2 border-[#00d4b1]/50 rounded-3xl text-white hover:bg-[#00d4b1]/20 transition-all shadow-[0_0_20px_rgba(0,212,177,0.1)] group"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-[#00d4b1] flex items-center justify-center text-white shadow-lg">
                  <MapPin size={20} fill="white" />
                </div>
                <span className="font-bold text-lg">{t('health_select_city')}</span>
              </div>
              <ChevronDown size={24} className={`text-[#00d4b1] transition-transform duration-300 ${showDropdown ? 'rotate-180' : ''}`} />
            </button>

            {showDropdown && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-[#020c18] border border-white/10 rounded-2xl shadow-2xl overflow-hidden max-h-[300px] overflow-y-auto z-50">
                {villes.map((v) => (
                  <button
                    key={v}
                    onClick={() => handleSelectVille(v)}
                    className="w-full text-left px-6 py-3 hover:bg-[#00d4b1]/10 text-white font-medium transition-colors"
                  >
                    {v}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="h-[120px] sm:hidden" />
      </main>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-[#ef4444] animate-spin" />
      </div>
    );
  }

  const rec = recommendations[0];
  const isCritical = rec?.niveau_risque === "CRITIQUE" || rec?.niveau_risque === "ÉLEVÉ";
  const globalColor = rec?.couleur || "#FFC107";

  return (
    <main className="p-6 pb-24 max-w-5xl mx-auto animate-in fade-in duration-700">
      <header className="mb-8">
        <HealthNav currentPage="personnes-agees" />
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-black text-white mb-1">{t('health_title_1')} {t('health_prof_seniors')}</h1>
            <p className="text-[#00d4b1] text-base font-bold flex items-center gap-2">
              <MapPin size={16} /> {ville}
            </p>
          </div>
          <button
            onClick={() => selectVille("")}
            className="px-6 py-3 bg-[#00d4b1] text-white font-black uppercase tracking-tighter text-xs rounded-2xl shadow-[0_4px_20px_rgba(0,212,177,0.4)] hover:bg-[#00b89c] hover:scale-105 transition-all active:scale-95 flex items-center gap-2 shrink-0 border border-white/20"
          >
            <MapPin size={16} fill="white" />
            {t('health_change_city')}
          </button>
        </div>
      </header>

      <div className={`glass-card mb-8 overflow-hidden relative border-2 ${isCritical ? 'border-red-500/50 shadow-[0_0_30px_rgba(239,68,68,0.3)]' : 'border-white/5'} transition-all`}>
        {isCritical && (
          <div className="bg-red-600 px-6 py-3 flex items-center gap-3">
            <AlertTriangle className="text-white" size={24} />
            <span className="text-white font-black text-lg tracking-wide">{t('health_alert_pollution').replace('{}', rec?.niveau_risque?.toUpperCase() || "")}</span>
          </div>
        )}
        <div className="p-6 md:p-8">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="text-7xl">{rec?.icone || "👴"}</div>
            <div className="flex-1 text-center md:text-left">
              <h3 className="text-2xl font-black text-white mb-2">{rec?.profil || t('health_prof_seniors')}</h3>
              <div className="inline-flex items-center gap-3 px-5 py-2 rounded-full border border-white/10 bg-white/5">
                <div className="w-3 h-3 rounded-full animate-pulse" style={{ backgroundColor: globalColor, boxShadow: `0 0 12px ${globalColor}` }} />
                <span className="text-base font-black uppercase tracking-[0.2em]" style={{ color: globalColor }}>
                  {t('health_level').replace('{}', rec?.niveau_risque || "MODÉRÉ")}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>


      <div className="glass-card p-6 mb-8 border-white/5">
        <h4 className="text-lg font-black text-white mb-4 flex items-center gap-2">
          <AlertTriangle className="text-amber-400" size={20} />
          {t('health_alert_msg')}
        </h4>
        <p className="text-lg text-white leading-relaxed font-medium">
          &quot;{rec?.message || t('health_loading')}&quot;
        </p>
      </div>

      <div className="glass-card p-6 border-white/5">
        <h4 className="text-lg font-black text-white mb-6 flex items-center gap-2">
          <ShieldCheck className="text-[#00d4b1]" size={20} />
          {t('health_priority_actions')}
        </h4>
        <div className="space-y-4">
          {rec?.actions.map((action, i) => (
            <div key={i} className="flex items-center gap-4 p-4 rounded-xl border bg-white/5 border-white/5">
              <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 bg-[#00d4b1]/20 text-[#00d4b1]">
                <ShieldCheck size={20} />
              </div>
              <span className="text-base font-bold text-gray-200">
                {action}
              </span>
            </div>
          ))}
        </div>
      </div>
      
      {isCritical && (
        <div className="mt-8 p-6 bg-red-500/10 rounded-3xl border border-red-500/30 flex items-center gap-6">
          <div className="w-14 h-14 rounded-2xl bg-red-500/20 flex items-center justify-center text-red-400 shrink-0">
            <AlertTriangle size={28} />
          </div>
          <div>
            <h5 className="text-red-400 font-black mb-1">{t('health_attention')}</h5>
            <p className="text-red-300/70 text-sm leading-relaxed">
              {t('health_ai_note')}
            </p>
          </div>
        </div>
      )}

      {/* ── Quick Switcher ── */}
      <div className="mt-16 p-10 glass-card border-white/5 flex flex-col items-center gap-8 relative overflow-hidden group">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#00d4b1]/30 to-transparent" />
        <div className="flex flex-col items-center gap-1">
          <h4 className="text-2xl font-black text-white">{t('health_continue_explore')}</h4>
          <p className="text-gray-400 text-sm font-medium">{t('health_discover_other')}</p>
        </div>

        <div className="flex flex-wrap justify-center gap-6 w-full">
          {[
            { title: t('health_prof_children'), icon: "👶", color: "from-blue-500/20 to-blue-600/5", border: "border-blue-500/30", text: "text-blue-400", href: "/dashboard/sante/enfants" },
            { title: t('health_prof_adults'), icon: "🧑", color: "from-green-500/20 to-green-600/5", border: "border-green-500/30", text: "text-green-400", href: "/dashboard/sante/adultes" },
            { title: t('health_prof_asthma'), icon: "🫁", color: "from-red-500/20 to-red-600/5", border: "border-red-500/30", text: "text-red-400", href: "/dashboard/sante/asmatiques" }
          ].map((profile) => (
            <button
              key={profile.title}
              onClick={() => router.push(profile.href)}
              className={`flex-1 min-w-[160px] p-6 rounded-[2rem] border-2 ${profile.border} bg-gradient-to-br ${profile.color} hover:scale-105 transition-all duration-300 flex flex-col items-center gap-3 active:scale-95 group/btn`}
            >
              <span className="text-4xl group-hover/btn:scale-110 transition-transform">{profile.icon}</span>
              <span className={`font-black text-sm uppercase tracking-tighter ${profile.text}`}>{profile.title}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="h-[120px] sm:hidden" />
    </main>
  );
}
