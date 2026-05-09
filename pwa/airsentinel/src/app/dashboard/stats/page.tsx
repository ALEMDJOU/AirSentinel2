"use client";

import { useEffect, useState } from "react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, Cell, PieChart, Pie 
} from "recharts";
import { TrendingUp, Activity, MapPin, Loader2, Award, Zap, Layers, AlertCircle } from "lucide-react";
import Image from "next/image";
import kpiService from "@/services/kpiService";
import mapService from "@/services/mapService";
import contexteService from "@/services/contexteService";
import { KPIResponse } from "@/types/pollution";
import { useVille } from "@/context/VilleContext";
import { useLanguage } from "@/context/LanguageContext";
import { RefreshCcw, XCircle } from "lucide-react";
import CitySelector from "@/components/CitySelector";

export default function StatsPage() {
  const { t } = useLanguage();
  const [kpis, setKpis] = useState<KPIResponse | null>(null);
  const [analyses, setAnalyses] = useState<any>(null);
  const [contexte, setContexte] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { ville, setVille } = useVille();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [kpiData, analysesData, contexteData] = await Promise.all([
          kpiService.getNationalKPIs(ville || undefined),
          mapService.getMapAnalyses(), // Toujours national pour le graphique régions
          contexteService.getContexte(ville || undefined)
        ]);
        setKpis(kpiData);
        setAnalyses(analysesData);
        setContexte(contexteData);
      } catch (err) {
        console.error("Erreur chargement stats:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [ville, t]);

  // isNational reste utile pour le header
  const isNational = !ville || ville === "CAMEROON";

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-[#00d4b1] animate-spin" />
      </div>
    );
  }

  // Si aucune ville n'est sélectionnée (ou sélection délibérée du National)
  // On peut décider de forcer le sélecteur si ville est strictement null ET que 
  // l'utilisateur n'a pas encore "dépassé" l'étape de sélection.
  // Pour rester simple et efficace : si ville est null, on affiche le sélecteur.
  // Si l'utilisateur clique sur "National" dans le sélecteur, on pourrait mettre 
  // une valeur spéciale comme "Cameroon" ou simplement autoriser l'affichage.

  return (
    <main className="relative min-h-screen overflow-x-hidden">
      {/* Background Section */}
      <div className="fixed inset-0 -z-10">
        <Image
          src="/joel3.jpg"
          alt="Statistiques Background"
          fill
          className="object-cover opacity-20 scale-105"
          priority
        />
        <div className="absolute inset-0 bg-[#020617]/90 backdrop-blur-[2px]" />
      </div>

      <div className="p-6 pb-64 max-w-6xl mx-auto relative z-10">
        {!ville ? (
          <div className="py-12">
            <header className="mb-12">
               <h1 className="text-5xl font-black text-white mb-3 tracking-tighter">
                 {t('footer_stats')} <span className="text-[#00d4b1]">{t('stats_analytics')}</span>
               </h1>
               <p className="text-gray-400 text-sm font-medium">{t('stats_explore_desc')}</p>
            </header>
            <CitySelector />
          </div>
        ) : (
          <>
            <header className="mb-12 animate-in fade-in slide-in-from-left duration-700">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-1 w-8 bg-[#00d4b1] rounded-full shadow-[0_0_10px_rgba(0,212,177,0.5)]" />
                  <span className="text-[10px] font-black tracking-[0.3em] text-[#00d4b1] uppercase">
                    {ville === "CAMEROON" ? t('stats_national') : t('stats_insights').replace('{}', ville)}
                  </span>
                </div>
                
                <button 
                  onClick={() => setVille(null)}
                  className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl text-[10px] font-bold text-gray-300 transition-all active:scale-95 group"
                >
                  <RefreshCcw size={14} className="text-[#00d4b1] group-hover:rotate-180 transition-transform duration-500" />
                  {t('stats_change_city')}
                </button>
              </div>
              
              <h1 className="text-5xl font-black text-white mb-3 tracking-tighter leading-none">
                {t('stats_analyse')} <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00d4b1] to-[#0ea5e9]">{ville === "CAMEROON" ? t('stats_data_nat') : t('stats_data_city').replace('{}', ville)}</span>
              </h1>
              <p className="text-gray-400 text-sm font-medium max-w-md antialiased">
                {ville === "CAMEROON" 
                  ? t('stats_desc_nat').replace('{x}', String(kpis?.total_observations || 0))
                  : t('stats_desc_city').replace('{y}', ville).replace('{x}', String(kpis?.total_observations || 0))
                }
              </p>
            </header>

            {/* Top KPIs Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <StatCard icon={<Activity />} label={t('stats_kpi_pm25')} value={kpis?.pm25_moyen || 0} unit="µg/m³" color="#00d4b1" />
              <StatCard icon={<TrendingUp />} label={t('stats_kpi_oms')} value={kpis?.villes_depassant_oms || 0} unit="" color="#ef4444" />
              <StatCard icon={<Zap />} label={t('stats_kpi_pol')} value={kpis?.polluant_dominant || "PM2.5"} unit="" color="#f59e0b" isText />
              <StatCard icon={<MapPin />} label={t('stats_kpi_pts')} value={kpis?.total_observations || 0} unit="" color="#0ea5e9" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              {/* Top Cities Table — col pleine largeur */}
              <div className="lg:col-span-2 glass-card p-8 border-white/5 border-l-4 border-l-[#ef4444]/50 flex flex-col">
                 <h3 className="text-xl font-bold text-white mb-6 tracking-tight">{t('stats_top5')}</h3>
                 <div className="space-y-4 flex-1 overflow-y-auto pr-2">
                    {analyses?.top_5_villes_critiques?.map((city: any, idx: number) => (
                       <div key={city.city} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 group hover:bg-white/10 transition-all duration-300">
                          <div className="flex items-center gap-4">
                             <span className="text-lg font-black text-[#ef4444]/40 group-hover:text-[#ef4444]">{idx + 1}</span>
                             <span className="text-sm font-bold text-gray-200">{city.city}</span>
                          </div>
                          <div className="flex flex-col items-end">
                             <span className="text-sm font-black text-white">{city.pm25_moyen}</span>
                             <span className="text-[8px] font-black text-[#ef4444] uppercase tracking-widest">µg/m³</span>
                          </div>
                       </div>
                    )) || <p className="text-center text-gray-500 py-10 italic">{t('stats_no_data')}</p>}
                 </div>
                 <div className="mt-8 p-4 bg-[#ef4444]/5 rounded-2xl border border-[#ef4444]/10">
                    <div className="flex items-center gap-3 mb-2">
                       <AlertCircle className="text-[#ef4444]" size={18} />
                       <span className="text-xs font-black text-[#ef4444] uppercase tracking-widest">{t('stats_alert')}</span>
                    </div>
                    <p className="text-[10px] text-gray-400 font-medium leading-relaxed">
                       {t('stats_alert_desc')}
                    </p>
                 </div>
              </div>

              {/* Polluants Mix */}
              <div className="glass-card p-8 border-white/5 relative group">
                 <div className="flex items-center gap-3 mb-6">
                    <Layers className="text-[#00d4b1]" size={20} />
                    <h3 className="text-lg font-bold text-white">{t('stats_mix')}</h3>
                 </div>
                 
                 <div className="space-y-5">
                   {contexte?.donut_polluants?.length > 0 ? (
                       contexte.donut_polluants.map((entry: any, index: number) => (
                          <div key={index} className="space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="text-xs font-bold text-gray-300">{entry.label}</span>
                              <span className="text-xs font-black text-white">{entry.valeur}%</span>
                            </div>
                            <div className="w-full h-2 rounded-full overflow-hidden bg-white/5 border border-white/5">
                               <div 
                                 className="h-full rounded-full transition-all duration-1000 relative"
                                 style={{ width: `${entry.valeur}%`, backgroundColor: entry.couleur }}
                               >
                                 <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white/30" />
                               </div>
                            </div>
                          </div>
                       ))
                   ) : (
                       <div className="flex items-center justify-center h-full min-h-[150px]">
                          <p className="text-gray-500 italic text-sm">{t('stats_no_multi')}</p>
                       </div>
                   )}
                 </div>
              </div>
            </div>
             <div className="h-[120px] sm:hidden" />
           </>
         )}
       </div>
     </main>
   );
 }

function StatCard({ icon, label, value, unit, color, isText }: any) {
  return (
    <div className="glass-card group p-5 flex flex-col gap-4 border-white/5 hover:border-white/10 transition-all duration-500">
      <div 
        className="w-10 h-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
        style={{ backgroundColor: `${color}15`, color: color }}
      >
        {icon}
      </div>
      <div>
        <div className={`font-black text-white tracking-tight ${isText ? 'text-2xl pt-1' : 'text-3xl'}`}>
          {value}
        </div>
        <div 
           className="text-[9px] font-black uppercase tracking-widest mt-1.5 flex items-center gap-1.5 opacity-80"
           style={{ color: color }}
        >
          {label} <span className="opacity-20">|</span> {unit}
        </div>
      </div>
    </div>
  );
}
