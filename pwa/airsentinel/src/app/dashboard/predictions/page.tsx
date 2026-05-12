"use client";

import { useEffect, useState } from "react";
import { 
  XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, AreaChart, Area, ReferenceLine 
} from "recharts";
import { Brain, Sparkles, AlertCircle, Loader2, TrendingUp, TrendingDown, Minus, RefreshCcw, Activity, CalendarDays, CalendarPlus } from "lucide-react";
import predictionService from "@/services/predictionService";
import { PredictionPoint } from "@/types/prediction";
import { useVille } from "@/context/VilleContext";
import { useLanguage } from "@/context/LanguageContext";
import CitySelector from "@/components/CitySelector";

export default function PredictionsPage() {
  const { ville, setVille } = useVille();
  const { t } = useLanguage();
  const [data, setData] = useState<PredictionPoint[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [features, setFeatures] = useState({
    dust: 45,
    co: 12,
    uv: 6,
    ozone: 30,
    temp: 28,
    humidity: 70
  });
  const [interactiveResult, setInteractiveResult] = useState<{
    predicted_pm25: number;
    level: string;
    color: string;
    description: string;
  } | null>(null);
  const [isComputing, setIsComputing] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPredictions = async () => {
      if (!ville || ville === "CAMEROON") {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const res = await predictionService.getShortTerm(ville);
        setData(res);
        
        // Initialiser les features du simulateur avec les valeurs réelles d'aujourd'hui
        const todayPoint = res.filter(p => !p.is_prediction).pop();
        if (todayPoint && todayPoint.features) {
          setFeatures({
            dust: todayPoint.features.dust || 0,
            co: todayPoint.features.co || 0,
            uv: todayPoint.features.uv || 0,
            ozone: todayPoint.features.ozone || 0,
            temp: todayPoint.features.temp || 0,
            humidity: todayPoint.features.humidity || 0
          });
        }
      } catch (err) {
        console.error("Erreur chargement prédictions:", err);
        setError(t('error_load'));
      } finally {
        setLoading(false);
      }
    };
    fetchPredictions();
  }, [ville, t]);

  // Déclenchement du calcul interactif
  useEffect(() => {
    const compute = async () => {
      if (!ville || ville === "CAMEROON") return;
      setIsComputing(true);
      setSimulationError(null);
      try {
        const res = await predictionService.computeInteractive(ville, features);
        setInteractiveResult(res);
      } catch (err) {
        console.error("Erreur simulation:", err);
        setSimulationError("Le service de simulation est temporairement indisponible.");
      } finally {
        setIsComputing(false);
      }
    };
    const timer = setTimeout(compute, 500); 
    return () => clearTimeout(timer);
  }, [ville, features, t]);

  const handleFeatureChange = (key: string, value: number) => {
    setFeatures(prev => ({ ...prev, [key]: value }));
  };


  // Extraction intelligente basée sur les dates réelles
  const todayStr = new Date().toISOString().split('T')[0];
  const tomorrowStr = new Date(Date.now() + 86400000).toISOString().split('T')[0];
  const afterTomorrowStr = new Date(Date.now() + 172800000).toISOString().split('T')[0];

  const today = data.find(p => p.date === todayStr) || data.filter(p => !p.is_prediction).pop();
  const jPlus1 = data.find(p => p.date === tomorrowStr);
  const jPlus2 = data.find(p => p.date === afterTomorrowStr);

  const lastReal = today?.pm25 || 25;
  const trendPct = jPlus1 ? ((jPlus1.pm25 - lastReal) / lastReal) * 100 : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-12 h-12 text-[var(--teal)] animate-spin" />
        <span className="text-[10px] font-black tracking-widest text-[var(--teal)]/50 uppercase">{t('loading_ai')}</span>
      </div>
    );
  }

  return (
    <main className="p-4 md:p-8 pb-32 max-w-7xl mx-auto space-y-10 animate-in fade-in duration-700">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div className="space-y-1">
           <div className="flex items-center gap-2 mb-2">
              <Brain className="text-[var(--teal)]" size={18} />
              <span className="text-[10px] font-black tracking-[0.3em] text-[var(--teal)]/60 uppercase">{t('pred_system')}</span>
           </div>
           <h1 className="text-4xl md:text-5xl font-black text-[var(--text-primary)] tracking-tighter">
             {t('pred_lab').split(' ')[0]} <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--teal)] to-[#0ea5e9]">
               {t('pred_lab').split(' ').slice(1).join(' ')}
             </span>
           </h1>
           <p className="text-[var(--text-secondary)]/60 text-sm font-medium">{t('pred_desc')}</p>
        </div>
        
        {ville && ville !== "CAMEROON" && (
          <div className="flex items-center gap-4 px-6 py-3 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-2xl">
            <div className="text-right">
                <div className="text-[9px] font-black text-[var(--text-secondary)]/50 uppercase tracking-widest">{t('pred_zone')}</div>
                <div className="text-lg font-black text-[var(--text-primary)]">{ville}</div>
            </div>
            <div className="w-px h-8 bg-[var(--border-color)]" />
            <button 
              onClick={() => setVille(null)}
              className="p-2 hover:bg-[var(--bg-primary)] rounded-xl transition-colors group"
              title={t('health_change_city')}
            >
              <RefreshCcw size={18} className="text-[var(--teal)] group-hover:rotate-180 transition-transform duration-500" />
            </button>
          </div>
        )}
      </header>

      {!ville || ville === "CAMEROON" ? (
        <div className="py-10">
          <CitySelector hideNational={true} />
        </div>
      ) : (
        <div className="space-y-10">
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center gap-3 text-red-500 text-sm font-bold animate-shake">
              <AlertCircle size={20} /> {error}
            </div>
          )}

          <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start animate-in zoom-in-95 duration-500">
            <div className="xl:col-span-8 group">
               <div className="glass-card overflow-hidden border-[#00d4b1]/10 hover:border-[#00d4b1]/30 transition-all duration-500">
                 <div className="p-8">
                   <div className="flex justify-between items-start mb-10">
                      <div className="space-y-1">
                         <div className="text-[10px] font-black text-[var(--text-secondary)] uppercase tracking-widest">{t('pred_trend')}</div>
                         <div className="text-4xl font-black text-[var(--text-primary)] tabular-nums">
                           {jPlus1?.pm25.toFixed(1)} <span className="text-xl font-light text-[var(--text-secondary)] opacity-40 italic">µg/m³</span>
                         </div>
                      </div>
                      <div className={`p-4 rounded-2xl border flex flex-col items-end backdrop-blur-md ${trendPct > 0 ? 'bg-orange-500/5 border-orange-500/20' : 'bg-[var(--teal)]/5 border-[var(--teal)]/20'}`}>
                         <span className="text-[10px] font-black text-[var(--text-secondary)]/50 uppercase">{t('pred_fluctuation')}</span>
                         <div className={`text-xl font-black flex items-center gap-2 ${trendPct > 0 ? 'text-orange-500' : 'text-[var(--teal)]'}`}>
                            {trendPct > 1 ? <TrendingUp size={20} /> : trendPct < -1 ? <TrendingDown size={20} /> : <Minus size={20} />}
                            {Math.abs(trendPct).toFixed(1)}%
                         </div>
                      </div>
                   </div>

                   <div className="h-[400px] min-h-[400px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                         <AreaChart data={data}>
                            <defs>
                               <linearGradient id="colorPm" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="var(--teal)" stopOpacity={0.4}/>
                                  <stop offset="95%" stopColor="var(--teal)" stopOpacity={0}/>
                               </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-color)" />
                            <XAxis 
                               dataKey="date" 
                               stroke="var(--text-secondary)"
                               fontSize={10}
                               tickFormatter={(val) => {
                                 const d = new Date(val);
                                 return isNaN(d.getTime()) ? "" : d.toLocaleDateString('fr', { day: '2-digit', month: 'short' });
                               }}
                               axisLine={false}
                               tickLine={false}
                               dy={10}
                            />
                            <YAxis 
                               stroke="var(--text-secondary)"
                               fontSize={10}
                               axisLine={false}
                               tickLine={false}
                               domain={['dataMin - 5', 'dataMax + 5']} 
                             />
                             <Tooltip 
                                contentStyle={{ 
                                  backgroundColor: 'var(--bg-secondary)', 
                                  border: '1px solid var(--border-color)', 
                                  borderRadius: '16px', 
                                  boxShadow: 'var(--shadow)',
                                  backdropFilter: 'blur(8px)'
                                }}
                                itemStyle={{ color: 'var(--teal)', fontWeight: '900' }}
                                labelStyle={{ color: 'var(--text-secondary)', fontSize: '10px', textTransform: 'uppercase', marginBottom: '4px' }}
                             />
                            <Area 
                               type="monotone" 
                               dataKey="pm25" 
                               stroke="var(--teal)" 
                               strokeWidth={5}
                               fillOpacity={1} 
                               fill="url(#colorPm)" 
                               animationDuration={3000}
                            />
                            {history.length > 0 && (
                               <ReferenceLine 
                                  x={history[history.length - 1]?.date} 
                                  stroke="var(--text-secondary)" 
                                  strokeDasharray="5 5" 
                                  label={{ value: 'PRÉDICTION IA', position: 'top', fill: 'var(--text-secondary)', fontSize: 8, fontWeight: 900 }} 
                               />
                            )}
                         </AreaChart>
                      </ResponsiveContainer>
                   </div>
                 </div>
               </div>
            </div>

            <div className="xl:col-span-4 space-y-6">
               {/* Cartes Aujourd'hui / Demain / Après-demain */}
               <div className="grid grid-cols-1 gap-4">
                  {/* Aujourd'hui */}
                  <div className="glass-card p-6 border-[var(--border-color)] flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="text-[9px] text-[var(--text-secondary)] font-black uppercase tracking-widest">{t('today')}</div>
                      <div className="text-3xl font-black text-[var(--text-primary)] tabular-nums">
                        {today?.pm25.toFixed(1) ?? "—"}
                        <span className="text-xs font-normal text-[var(--text-secondary)] ml-1">µg/m³</span>
                      </div>
                    </div>
                    <div className="w-12 h-12 rounded-2xl bg-[#00d4b1]/10 flex items-center justify-center text-[#00d4b1]">
                      <Activity size={24} />
                    </div>
                  </div>

                  {/* Demain */}
                  <div className="glass-card p-6 border-[var(--border-color)] flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="text-[9px] text-[var(--text-secondary)] font-black uppercase tracking-widest">{t('tomorrow')} (J+1)</div>
                      <div className="text-3xl font-black text-[var(--text-primary)] tabular-nums">
                        {jPlus1?.pm25.toFixed(1) ?? "—"}
                        <span className="text-xs font-normal text-[var(--text-secondary)] ml-1">µg/m³</span>
                      </div>
                    </div>
                    <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-500">
                      <CalendarDays size={24} />
                    </div>
                  </div>

                  {/* Après-demain */}
                  <div className="glass-card p-6 border-[var(--border-color)] flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="text-[9px] text-[var(--text-secondary)] font-black uppercase tracking-widest">{t('after_tomorrow_j2')} (J+2)</div>
                      <div className="text-3xl font-black text-[var(--text-primary)] tabular-nums">
                        {jPlus2?.pm25.toFixed(1) ?? "—"}
                        <span className="text-xs font-normal text-[var(--text-secondary)] ml-1">µg/m³</span>
                      </div>
                    </div>
                    <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                      <CalendarPlus size={24} />
                    </div>
                  </div>
               </div>
            </div>
          </div>

          <section className="glass-card p-1 border-[var(--teal)]/30 overflow-hidden group">
            <div className="bg-[var(--bg-secondary)] rounded-[inherit] overflow-hidden">
               <div className="p-8 md:p-12">
                  <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8 mb-16">
                     <div className="space-y-2">
                        <div className="flex items-center gap-3">
                           <Sparkles className="text-[var(--teal)] animate-pulse" size={24} />
                           <h2 className="text-4xl font-black text-[var(--text-primary)] tracking-tighter"><span className="text-[var(--teal)]">{t('sim_lab_control')}</span></h2>
                        </div>
                        <p className="text-[var(--text-secondary)] text-sm font-medium">{t('sim_lab_desc').replace('{ville}', ville)}</p>
                     </div>
                  </header>

                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
                     <div className="lg:col-span-7 grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10">
                        {[
                          { id: 'dust', label: t('sim_param_dust'), min: 0, max: 300, unit: 'µg', icon: '🌪️', color: '#f59e0b' },
                          { id: 'co', label: t('sim_param_traffic'), min: 0, max: 40, unit: 'ppm', icon: '🚗', color: '#3b82f6' },
                          { id: 'uv', label: t('sim_param_uv'), min: 0, max: 15, unit: 'idx', icon: '☀️', color: '#eab308' },
                          { id: 'temp', label: t('sim_param_temp'), min: 15, max: 45, unit: '°C', icon: '🌡️', color: '#ef4444' },
                          { id: 'humidity', label: t('sim_param_hum'), min: 0, max: 100, unit: '%', icon: '💧', color: '#0ea5e9' },
                          { id: 'ozone', label: t('sim_param_ozone'), min: 0, max: 200, unit: 'µg', icon: '☁️', color: '#8b5cf6' },
                        ].map((f) => (
                          <div key={f.id} className="space-y-4 group/slider">
                             <div className="flex justify-between items-center">
                                <label className="text-[10px] font-black uppercase text-[var(--text-secondary)]/50 tracking-wider flex items-center gap-2">
                                   <span className="text-base grayscale opacity-50 group-hover/slider:grayscale-0 group-hover/slider:opacity-100 transition-all">{f.icon}</span>
                                   {f.label}
                                </label>
                                <span className="text-sm font-black text-[var(--text-primary)] tabular-nums px-3 py-1 bg-[var(--bg-primary)]/50 rounded-lg border border-[var(--border-color)]">{features[f.id as keyof typeof features]} {f.unit}</span>
                             </div>
                             <div className="relative flex items-center">
                                <input 
                                   type="range"
                                   min={f.min}
                                   max={f.max}
                                   value={features[f.id as keyof typeof features]}
                                   onChange={(e) => handleFeatureChange(f.id, parseFloat(e.target.value))}
                                   className="w-full h-2 bg-[var(--bg-primary)] rounded-full appearance-none cursor-pointer accent-[var(--teal)] hover:accent-[var(--blue-deep)] transition-all border border-[var(--border-color)]"
                                   style={{ '--thumb-color': f.color } as React.CSSProperties}
                                />
                             </div>
                          </div>
                        ))}
                     </div>

                     <div className="lg:col-span-5">
                        <div className="relative h-full flex flex-col justify-center">
                           <div 
                             className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-64 blur-[100px] opacity-20 transition-colors duration-1000"
                             style={{ backgroundColor: interactiveResult?.color || '#00d4b1' }}
                           />

                           <div className="relative glass-card border-[var(--border-color)] p-10 flex flex-col items-center text-center backdrop-blur-3xl bg-[var(--bg-secondary)]/80 shadow-2xl">
                              <div className="text-[10px] font-black text-[var(--text-secondary)]/50 uppercase tracking-[0.4em] mb-8">{t('sim_est_realtime')}</div>
                              
                              {isComputing ? (
                                <div className="h-[200px] flex flex-col items-center justify-center gap-4">
                                   <Loader2 className="w-16 h-16 text-[#00d4b1] animate-spin" />
                                   <span className="text-[9px] font-black text-[#00d4b1] uppercase animate-pulse">{t('sim_calc')}</span>
                                </div>
                              ) : simulationError ? (
                                <div className="h-[200px] flex flex-col items-center justify-center gap-4 text-red-500">
                                   <AlertCircle size={40} className="opacity-50" />
                                   <span className="text-xs font-bold max-w-[200px]">{simulationError}</span>
                                   <button 
                                     onClick={() => setFeatures({...features})} 
                                     className="text-[9px] font-black uppercase underline tracking-widest mt-2"
                                   >
                                     {t('sim_retry')}
                                   </button>
                                </div>
                              ) : (
                                 <div className="space-y-6 animate-in zoom-in-95 duration-500">
                                   <div className="relative inline-block">
                                      <div className="text-6xl font-black text-[var(--text-primary)] tracking-tighter tabular-nums drop-shadow-[0_10px_30px_rgba(255,255,255,0.1)]">
                                        {interactiveResult?.predicted_pm25.toFixed(1)}
                                      </div>
                                      <div className="absolute -right-12 top-2 text-2xl font-light text-[var(--text-secondary)]/50 italic uppercase">µg/m³</div>
                                   </div>

                                   <div 
                                     className="mx-auto px-8 py-3 rounded-full font-black text-white text-base uppercase tracking-widest shadow-2xl transition-all duration-700"
                                     style={{ backgroundColor: interactiveResult?.color, boxShadow: `0 0 30px ${interactiveResult?.color}44` }}
                                   >
                                     {interactiveResult?.level}
                                   </div>

                                   <p className="text-[var(--text-secondary)] text-sm max-w-xs leading-relaxed font-medium mx-auto">
                                     {interactiveResult?.description}
                                   </p>
                                </div>
                              )}

                              <footer className="mt-12 pt-10 border-t border-[var(--border-color)] w-full grid grid-cols-2 gap-4">
                                 <div className="space-y-1">
                                    <div className="text-[9px] text-[var(--text-secondary)]/50 uppercase font-black tracking-widest">{t('sim_db')}</div>
                                    <div className="text-xs font-bold text-[var(--text-primary)] uppercase italic tracking-tighter">Cameroun-V12</div>
                                 </div>
                                 <div className="space-y-1">
                                    <div className="text-[9px] text-[var(--text-secondary)]/50 uppercase font-black tracking-widest">{t('sim_ai_precision')}</div>
                                    <div className="text-xs font-bold text-[var(--teal)]">± 1.4 µg</div>
                                 </div>
                              </footer>
                           </div>
                        </div>
                     </div>
                  </div>
               </div>
            </div>
          </section>

          <div className="h-[40px] xl:hidden" />
        </div>
      )}
    </main>
  );
}
