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
  const { t, lang } = useLanguage();
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
        setSimulationError(t('sim_error'));
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


  const predictions = data.filter(p => p.is_prediction);
  const history = data.filter(p => !p.is_prediction);
  const today = history[history.length - 1];   // Aujourd'hui = dernière valeur réelle
  const jPlus1 = predictions[0];               // Demain
  const jPlus2 = predictions[1];               // Après-demain
  const lastReal = today?.pm25 || 0;
  const trendPct = jPlus1 ? ((jPlus1.pm25 - lastReal) / lastReal) * 100 : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-12 h-12 text-[#00d4b1] animate-spin" />
        <span className="text-[10px] font-black tracking-widest text-[#00d4b1]/50 uppercase">{t('loading_ai')}</span>
      </div>
    );
  }

  return (
    <main className="p-4 md:p-8 pb-32 max-w-7xl mx-auto space-y-10 animate-in fade-in duration-700">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div className="space-y-1">
           <div className="flex items-center gap-2 mb-2">
              <Brain className="text-[#00d4b1]" size={18} />
              <span className="text-[10px] font-black tracking-[0.3em] text-[#00d4b1]/60 uppercase">{t('pred_system')}</span>
           </div>
           <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter">
             {t('pred_lab').split(' ')[0]} <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00d4b1] to-[#0ea5e9]">
               {t('pred_lab').split(' ').slice(1).join(' ')}
             </span>
           </h1>
           <p className="text-[#e0f2fe]/40 text-sm font-medium">{t('pred_desc')}</p>
        </div>
        
        {ville && ville !== "CAMEROON" && (
          <div className="flex items-center gap-4 px-6 py-3 bg-white/5 border border-white/10 rounded-2xl">
            <div className="text-right">
                <div className="text-[9px] font-black text-gray-500 uppercase tracking-widest">{t('pred_zone')}</div>
                <div className="text-lg font-black text-white">{ville}</div>
            </div>
            <div className="w-px h-8 bg-white/10" />
            <button 
              onClick={() => setVille(null)}
              className="p-2 hover:bg-white/10 rounded-xl transition-colors group"
              title={t('health_change_city')}
            >
              <RefreshCcw size={18} className="text-[#00d4b1] group-hover:rotate-180 transition-transform duration-500" />
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
                         <div className="text-[10px] font-black text-gray-500 uppercase tracking-widest">{t('pred_trend')}</div>
                         <div className="text-4xl font-black text-white tabular-nums">
                           {jPlus1?.pm25.toFixed(1)} <span className="text-xl font-light opacity-30 italic">µg/m³</span>
                         </div>
                      </div>
                      <div className={`p-4 rounded-2xl border flex flex-col items-end backdrop-blur-md ${trendPct > 0 ? 'bg-orange-500/5 border-orange-500/20' : 'bg-[#00d4b1]/5 border-[#00d4b1]/20'}`}>
                         <span className="text-[10px] font-black text-gray-500 uppercase">{t('pred_fluctuation')}</span>
                         <div className={`text-xl font-black flex items-center gap-2 ${trendPct > 0 ? 'text-orange-500' : 'text-[#00d4b1]'}`}>
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
                                  <stop offset="5%" stopColor="#00d4b1" stopOpacity={0.4}/>
                                  <stop offset="95%" stopColor="#00d4b1" stopOpacity={0}/>
                               </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
                            <XAxis 
                               dataKey="date" 
                               stroke="#475569"
                               fontSize={10}
                               tickFormatter={(val) => new Date(val).toLocaleDateString(lang, { day: '2-digit', month: 'short' })}
                               axisLine={false}
                               tickLine={false}
                               dy={10}
                            />
                            <YAxis 
                              stroke="#475569"
                              fontSize={10}
                              axisLine={false}
                              tickLine={false}
                              domain={['dataMin - 5', 'dataMax + 5']} 
                            />
                            <Tooltip 
                               contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.5)' }}
                               itemStyle={{ color: '#00d4b1', fontWeight: '900' }}
                               labelStyle={{ color: '#94a3b8', fontSize: '10px', textTransform: 'uppercase', marginBottom: '4px' }}
                            />
                            <Area 
                               type="monotone" 
                               dataKey="pm25" 
                               stroke="#00d4b1" 
                               strokeWidth={5}
                               fillOpacity={1} 
                               fill="url(#colorPm)" 
                               animationDuration={3000}
                            />
                            {history.length > 0 && (
                               <ReferenceLine 
                                  x={history[history.length-1].date} 
                                  stroke="#64748b" 
                                  strokeDasharray="5 5" 
                                  label={{ value: t('chart_ai_prediction'), position: 'top', fill: '#64748b', fontSize: 8, fontWeight: 900 }} 
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
                  <div className="glass-card p-6 border-white/5 flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="text-[9px] text-gray-500 font-black uppercase tracking-widest">{t('today')}</div>
                      <div className="text-3xl font-black text-white tabular-nums">
                        {today?.pm25.toFixed(1) ?? "—"}
                        <span className="text-xs font-normal text-gray-500 ml-1">µg/m³</span>
                      </div>
                    </div>
                    <div className="w-12 h-12 rounded-2xl bg-[#00d4b1]/10 flex items-center justify-center text-[#00d4b1]">
                      <Activity size={24} />
                    </div>
                  </div>

                  {/* Demain */}
                  <div className="glass-card p-6 border-white/5 flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="text-[9px] text-gray-500 font-black uppercase tracking-widest">{t('tomorrow')} (J+1)</div>
                      <div className="text-3xl font-black text-white tabular-nums">
                        {jPlus1?.pm25.toFixed(1) ?? "—"}
                        <span className="text-xs font-normal text-gray-500 ml-1">µg/m³</span>
                      </div>
                    </div>
                    <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center text-blue-500">
                      <CalendarDays size={24} />
                    </div>
                  </div>

                  {/* Après-demain */}
                  <div className="glass-card p-6 border-white/5 flex items-center justify-between">
                    <div className="space-y-1">
                      <div className="text-[9px] text-gray-500 font-black uppercase tracking-widest">{t('after_tomorrow_j2')} (J+2)</div>
                      <div className="text-3xl font-black text-white tabular-nums">
                        {jPlus2?.pm25.toFixed(1) ?? "—"}
                        <span className="text-xs font-normal text-gray-500 ml-1">µg/m³</span>
                      </div>
                    </div>
                    <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                      <CalendarPlus size={24} />
                    </div>
                  </div>
               </div>
            </div>
          </div>

          <section className="glass-card p-1 border-[#00d4b1]/30 overflow-hidden group">
            <div className="bg-slate-900/50 rounded-[inherit] overflow-hidden">
               <div className="p-8 md:p-12">
                  <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8 mb-16">
                     <div className="space-y-2">
                        <div className="flex items-center gap-3">
                           <Sparkles className="text-[#00d4b1] animate-pulse" size={24} />
                           <h2 className="text-4xl font-black text-white tracking-tighter"><span className="text-[#00d4b1]">{t('sim_lab_control')}</span></h2>
                        </div>
                        <p className="text-gray-400 text-sm font-medium">{t('sim_lab_desc').replace('{ville}', ville)}</p>
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
                                <label className="text-[10px] font-black uppercase text-gray-500 tracking-wider flex items-center gap-2">
                                   <span className="text-base grayscale opacity-50 group-hover/slider:grayscale-0 group-hover/slider:opacity-100 transition-all">{f.icon}</span>
                                   {f.label}
                                </label>
                                <span className="text-sm font-black text-white tabular-nums px-3 py-1 bg-white/5 rounded-lg border border-white/5">{features[f.id as keyof typeof features]} {f.unit}</span>
                             </div>
                             <div className="relative flex items-center">
                                <input 
                                   type="range"
                                   min={f.min}
                                   max={f.max}
                                   value={features[f.id as keyof typeof features]}
                                   onChange={(e) => handleFeatureChange(f.id, parseFloat(e.target.value))}
                                   className="w-full h-2 bg-[#020617] rounded-full appearance-none cursor-pointer accent-[#00d4b1] hover:accent-[#0ea5e9] transition-all border border-white/5"
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

                           <div className="relative glass-card border-white/10 p-10 flex flex-col items-center text-center backdrop-blur-3xl bg-slate-900/60 shadow-2xl">
                              <div className="text-[10px] font-black text-gray-500 uppercase tracking-[0.4em] mb-8">{t('sim_est_realtime')}</div>
                              
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
                                      <div className="text-6xl font-black text-white tracking-tighter tabular-nums drop-shadow-[0_10px_30px_rgba(255,255,255,0.1)]">
                                        {interactiveResult?.predicted_pm25.toFixed(1)}
                                      </div>
                                      <div className="absolute -right-12 top-2 text-2xl font-light text-gray-500 italic uppercase">µg/m³</div>
                                   </div>

                                   <div 
                                     className="mx-auto px-8 py-3 rounded-full font-black text-white text-base uppercase tracking-widest shadow-2xl transition-all duration-700"
                                     style={{ backgroundColor: interactiveResult?.color, boxShadow: `0 0 30px ${interactiveResult?.color}44` }}
                                   >
                                     {interactiveResult?.level}
                                   </div>

                                   <p className="text-gray-400 text-sm max-w-xs leading-relaxed font-medium mx-auto">
                                     {interactiveResult?.description}
                                   </p>
                                </div>
                              )}

                              <footer className="mt-12 pt-10 border-t border-white/10 w-full grid grid-cols-2 gap-4">
                                 <div className="space-y-1">
                                    <div className="text-[9px] text-gray-500 uppercase font-black tracking-widest">{t('sim_db')}</div>
                                    <div className="text-xs font-bold text-white uppercase italic tracking-tighter">Cameroun-V12</div>
                                 </div>
                                 <div className="space-y-1">
                                    <div className="text-[9px] text-gray-500 uppercase font-black tracking-widest">{t('sim_ai_precision')}</div>
                                    <div className="text-xs font-bold text-[#00d4b1]">± 1.4 µg</div>
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
