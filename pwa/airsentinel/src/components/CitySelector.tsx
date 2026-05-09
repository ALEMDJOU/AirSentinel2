"use client";

import { useEffect, useState } from "react";
import { Search, MapPin, Loader2, Globe } from "lucide-react";
import mapService from "@/services/mapService";
import { VillePoint } from "@/types/map";
import { useVille } from "@/context/VilleContext";
import { useLanguage } from "@/context/LanguageContext";

interface CitySelectorProps {
  hideNational?: boolean;
}

export default function CitySelector({ hideNational = false }: CitySelectorProps) {
  const [cities, setCities] = useState<VillePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const { ville, setVille } = useVille();
  const { t } = useLanguage();

  useEffect(() => {
    const fetchCities = async () => {
      try {
        const data = await mapService.getMapPoints();
        // Sort alphabetically
        setCities(data.sort((a, b) => a.city.localeCompare(b.city)));
      } catch (err) {
        console.error("Erreur chargement villes:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCities();
  }, []);

  const filteredCities = cities.filter((c) =>
    c.city.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <Loader2 className="w-10 h-10 text-[#00d4b1] animate-spin" />
        <span className="text-[10px] font-black tracking-widest text-[#00d4b1]/50 uppercase">{t('city_loading')}</span>
      </div>
    );
  }

  return (
    <section className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1">
          <h2 className="text-3xl font-black text-white tracking-tight">{t('city_selector_title')}</h2>
          <p className="text-gray-400 text-sm font-medium">{t('city_selector_desc')}</p>
        </div>

        <div className="relative group max-w-sm w-full">
          <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-[#00d4b1] transition-colors" size={18} />
          <input
            type="text"
            placeholder={t('city_search_placeholder')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-14 pr-6 text-white text-sm font-bold focus:border-[#00d4b1] outline-none transition-all placeholder:text-gray-600"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {/* National Option */}
        {!search && !hideNational && (
          <button
            onClick={() => setVille("CAMEROON")}
            className="glass-card p-6 border-white/5 hover:border-[#0ea5e9]/30 hover:bg-[#0ea5e9]/5 transition-all duration-300 flex flex-col items-center text-center gap-3 group"
          >
            <div className="w-12 h-12 rounded-2xl bg-[#0ea5e9]/10 flex items-center justify-center text-[#0ea5e9] group-hover:scale-110 transition-transform shadow-[0_0_20px_rgba(14,165,233,0.1)]">
              <span className="text-[10px] font-black group-hover:scale-125 transition-transform"><Globe size={24} /></span>
            </div>
            <span className="text-xs font-black text-white uppercase tracking-wider group-hover:text-[#0ea5e9]">{t('city_national')}</span>
          </button>
        )}

        {filteredCities.map((city) => (
          <button
            key={city.city}
            onClick={() => setVille(city.city)}
            className="glass-card p-6 border-white/5 hover:border-[#00d4b1]/30 hover:bg-[#00d4b1]/5 transition-all duration-300 flex flex-col items-center text-center gap-3 group relative overflow-hidden"
          >
            {/* Status Indicator Glow */}
            <div 
              className="absolute -right-4 -top-4 w-12 h-12 blur-2xl opacity-20"
              style={{ backgroundColor: city.irs_color || '#64748b' }}
            />
            
            <div 
              className="w-12 h-12 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-xl"
              style={{ 
                backgroundColor: city.irs_color ? `${city.irs_color}15` : 'rgba(100, 116, 139, 0.1)', 
                color: city.irs_color || '#64748b' 
              }}
            >
              <MapPin size={24} />
            </div>
            <div className="space-y-1">
              <span className="text-xs font-black text-white uppercase tracking-tight block group-hover:text-[#00d4b1]">{city.city}</span>
              <div className="flex items-center justify-center gap-1">
                <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: city.irs_color || '#64748b' }} />
                <span className="text-[8px] font-black uppercase text-gray-500 tracking-widest">{city.irs_label || 'Actif'}</span>
              </div>
            </div>
          </button>
        ))}
      </div>

      {filteredCities.length === 0 && (
        <div className="py-20 text-center space-y-4">
          <div className="text-gray-600 font-black text-6xl opacity-10 uppercase tracking-tighter">{t('city_empty')}</div>
          <p className="text-gray-500 font-medium">{t('city_not_found').replace('{}', search)}</p>
        </div>
      )}
    </section>
  );
}
