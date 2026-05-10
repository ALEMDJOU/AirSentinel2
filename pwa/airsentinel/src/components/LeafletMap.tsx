"use client";

import { useEffect, useState, useCallback } from "react";
import L from "leaflet";
import { 
  MapContainer, 
  TileLayer, 
  CircleMarker, 
  Popup, 
  Tooltip as LeafletTooltip,
  LayersControl,
  useMap
} from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import { Navigation, Search, ZoomIn, ZoomOut, X, MapPin, Compass, Loader2, ThermometerSun, Wind } from "lucide-react";
import "leaflet/dist/leaflet.css";
import "leaflet.heat";
import { useRouter } from "next/navigation";

import mapService from "../services/mapService";
import { VillePoint } from "../types/map";
import { useVille } from "../context/VilleContext";
import { useLanguage } from "../context/LanguageContext";

// ── Sous-composant : REAL HEATMAP LAYER ──────────────────────────────────────

function HeatmapLayer({ points }: { points: VillePoint[] }) {
  const map = useMap();

  useEffect(() => {
    if (points.length === 0) return;
    
    const heatData: [number, number, number][] = points
      .filter(p => p.lat !== null && p.lon !== null)
      .map(c => [c.lat!, c.lon!, c.pm25_moyen / 100]);
      
    // @ts-expect-error - Leaflet.heat plugin not typed
    const heatLayer = L.heatLayer(heatData, {
      radius: 40,
      blur: 25,
      maxZoom: 14,
      gradient: { 0.2: 'green', 0.4: 'yellow', 0.6: 'orange', 0.8: 'red', 1.0: 'purple' }
    });

    heatLayer.addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [map, points]);

  return null;
}

// ── Sous-composant : PWA SEARCH BAR ─────────────────────────────────────────

function MapSearch({ points, onSelect, onSelectVille }: { points: VillePoint[], onSelect: (lat: number, lon: number) => void, onSelectVille: (ville: string) => void }) {
  const { t } = useLanguage();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<VillePoint[]>([]);

  const handleSearch = (val: string) => {
    setQuery(val);
    if (val.length > 1) {
      setResults(points.filter(c => c.city.toLowerCase().includes(val.toLowerCase())));
    } else {
      setResults([]);
    }
  };

  return (
    <div className="absolute top-[70px] left-0 right-0 z-[1000] flex justify-center px-4 pointer-events-none">
      <div className="w-full max-w-[400px] pointer-events-auto">
        <div className="relative group">
          <div className="absolute inset-x-0 -bottom-1 h-px bg-gradient-to-r from-transparent via-[#00d4b1]/50 to-transparent blur-sm opacity-0 group-focus-within:opacity-100 transition-opacity"></div>
          <div className="flex items-center bg-white border border-gray-100 rounded-3xl shadow-[0_15px_40px_rgba(0,0,0,0.12)] px-5 py-4 placeholder:text-gray-400">
            <Search size={22} className="text-[#00d4b1] mr-3 shrink-0" />
            <input
              type="text"
              placeholder={t('map_search_placeholder')}
              value={query}
              onChange={(e) => handleSearch(e.target.value)}
              className="bg-transparent border-none outline-none text-gray-800 text-base font-medium w-full placeholder:text-gray-400"
            />
            {query && (
              <button 
                onClick={() => handleSearch("")}
                className="p-1 hover:bg-gray-50 rounded-full"
              >
                <X size={20} className="text-gray-400" />
              </button>
            )}
          </div>

          {results.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-3 bg-white/95 backdrop-blur-xl border border-white/30 rounded-3xl shadow-2xl overflow-hidden py-2 max-h-[60vh] overflow-y-auto animate-in fade-in slide-in-from-top-2 duration-300">
              {results.map((point) => (
                <button
                  key={point.city}
                  onClick={() => {
                    onSelectVille(point.city);
                    if (point.lat && point.lon) onSelect(point.lat, point.lon);
                    setQuery("");
                    setResults([]);
                  }}
                  className="w-full text-left px-6 py-4 hover:bg-[#00d4b1]/5 flex items-center gap-4 transition-colors group border-b border-gray-50 last:border-0"
                >
                  <div className="w-10 h-10 rounded-xl bg-[#00d4b1]/10 flex items-center justify-center text-[#00d4b1] shrink-0">
                    <MapPin size={20} />
                  </div>
                  <div>
                    <div className="text-sm font-bold text-gray-800">{point.city}</div>
                    <div className="text-[10px] text-gray-500 font-bold uppercase tracking-tight flex items-center gap-2">
                        PM2.5: <span className="text-[#00d4b1]">{point.pm25_moyen} µg/m³</span>
                        <span className="w-1 h-1 rounded-full bg-gray-200"></span>
                        {point.irs_label || t('quality')}
                     </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Sous-composant : PWA OVERLAY CONTROLS ───────────────────────────────────

function MapOverlayControls({ map }: { map: L.Map | null }) {
  const { t } = useLanguage();
  const [locating, setLocating] = useState(false);

  const handleZoomIn = () => map?.zoomIn();
  const handleZoomOut = () => map?.zoomOut();

  const handleLocate = useCallback(() => {
    if (!map) return;
    if (!navigator.geolocation) {
      alert(t('map_geo_unsupported'));
      return;
    }
    
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocating(false);
        const { latitude, longitude } = position.coords;
        map.flyTo([latitude, longitude], 14, { animate: true, duration: 1.5 });
      },
      (error) => {
        setLocating(false);
        console.error("Geolocation error:", error);
        alert(t('map_geo_error'));
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  }, [map]);

  const handleReset = () => {
    map?.flyTo([ cameroonCenter[0], cameroonCenter[1] ], 6, { animate: true, duration: 1.2 });
  };
  const cameroonCenter: [number, number] = [7.3697, 12.3547];

  return (
    <div className="absolute bottom-28 right-6 z-[1001] flex flex-col gap-4 items-center">
      <div className="flex flex-col gap-3">
        <button
          onClick={handleLocate}
          disabled={locating}
          className={`w-14 h-14 bg-[#00d4b1] text-white rounded-2xl shadow-xl flex items-center justify-center transition-all active:scale-90 ${locating ? 'opacity-70' : ''}`}
        >
          <Navigation size={26} fill="white" className={locating ? 'animate-spin' : ''} />
        </button>
        
        <button
          onClick={handleReset}
          className="w-14 h-14 bg-white text-[#00d4b1] rounded-2xl shadow-xl flex items-center justify-center border border-gray-100 transition-all active:scale-95"
        >
          <Compass size={26} />
        </button>
      </div>

      <div className="flex flex-col bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden divide-y divide-gray-50">
        <button onClick={handleZoomIn} className="w-14 h-14 flex items-center justify-center text-gray-700 hover:bg-gray-50 active:bg-gray-100 transition-all">
          <ZoomIn size={24} strokeWidth={2.5} />
        </button>
        <button onClick={handleZoomOut} className="w-14 h-14 flex items-center justify-center text-gray-700 hover:bg-gray-50 active:bg-gray-100 transition-all">
          <ZoomOut size={24} strokeWidth={2.4} />
        </button>
      </div>
    </div>
  );
}

// ── Composant Principal ──────────────────────────────────────────────────────

// Niveaux de qualité OMS 2021 pour le filtre
const LEVELS = [
  { key: "ALL",       color: "#94a3b8" },
  { key: "EXCELLENT", color: "#008000" },
  { key: "BON",       color: "#4CAF50" },
  { key: "MODERE",    color: "#FFC107" },
  { key: "DEGRADE",   color: "#FF9800" },
  { key: "MAUVAIS",   color: "#FF5722" },
  { key: "CRITIQUE",  color: "#B71C1C" },
] as const;

type LevelKey = typeof LEVELS[number]["key"];

function getPointLevel(pm25: number): LevelKey {
  if (pm25 <= 5)   return "EXCELLENT";
  if (pm25 <= 15)  return "BON";
  if (pm25 <= 25)  return "MODERE";
  if (pm25 <= 50)  return "DEGRADE";
  if (pm25 <= 100) return "MAUVAIS";
  return "CRITIQUE";
}

function getPointColor(pm25: number): string {
  if (pm25 <= 5)   return "#008000";
  if (pm25 <= 15)  return "#4CAF50";
  if (pm25 <= 25)  return "#FFC107";
  if (pm25 <= 50)  return "#FF9800";
  if (pm25 <= 100) return "#FF5722";
  return "#B71C1C";
}

export default function LeafletMap() {
  const { t } = useLanguage();
  const cameroonCenter: [number, number] = [7.3697, 12.3547];
  const [map, setMap] = useState<L.Map | null>(null);
  const [points, setPoints] = useState<VillePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState<LevelKey>("ALL");
  const { selectVille } = useVille();
  const router = useRouter();

  useEffect(() => {
    const fetchPoints = async () => {
      try {
        const data = await mapService.getMapPoints();
        setPoints(data);
      } catch (err) {
        console.error("Erreur chargement points carte:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPoints();
  }, []);

  useEffect(() => {
    // @ts-expect-error - Leaflet internal method for icon URLs
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    });
  }, []);

  const handleSelectCity = (lat: number, lon: number) => {
    map?.flyTo([lat, lon], 12, { animate: true, duration: 1.5 });
  };

  // Points filtrés selon le niveau actif
  const filteredPoints = points.filter(p =>
    p.lat !== null && p.lon !== null &&
    (activeFilter === "ALL" || getPointLevel(p.pm25_moyen) === activeFilter)
  );

  // Comptage par niveau pour le filtre cliquable de la légende
  const countByLevel = (key: LevelKey) =>
    key === "ALL" ? points.length : points.filter(p => getPointLevel(p.pm25_moyen) === key).length;

  return (
    <div className="w-full h-full relative overflow-hidden">
      <MapSearch points={points} onSelect={handleSelectCity} onSelectVille={selectVille} />
      <MapOverlayControls map={map} />

      {loading && (
        <div className="absolute inset-0 z-[2000] bg-[#020c18]/40 backdrop-blur-sm flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
             <Loader2 className="w-10 h-10 text-[#00d4b1] animate-spin" />
             <p className="text-white text-sm font-medium">{t('map_sync')}</p>
          </div>
        </div>
      )}

      <MapContainer 
        center={cameroonCenter} 
        zoom={6} 
        minZoom={3}
        maxZoom={18}
        zoomControl={false}
        ref={(instance) => { if (instance) setMap(instance); }}
        style={{ width: "100%", height: "100%" }}
        className="bg-[#020c18] !z-0"
      >
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name={t('map_plan')}>
            <TileLayer
              attribution='&copy; OpenStreetMap'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name={t('map_sat')}>
            <TileLayer
              attribution='&copy; Esri'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            />
          </LayersControl.BaseLayer>

          <LayersControl.Overlay checked name={t('map_heatmap')}>
            <HeatmapLayer points={filteredPoints} />
          </LayersControl.Overlay>

           <LayersControl.Overlay checked name={t('map_stations')}>
               {filteredPoints.map((point) => {
                  const color = getPointColor(point.pm25_moyen);
                  const pm25Label = t(getPointLevel(point.pm25_moyen));
                  const pm25Value = point.pm25_moyen.toFixed(1);
                 
                 return (
                   <CircleMarker
                     key={point.city}
                     center={[point.lat!, point.lon!]}
                     radius={8}
                     pathOptions={{
                       fillColor: color,
                       color: "white",
                       weight: 3,
                       fillOpacity: 0.9,
                     }}
                     eventHandlers={{
                       click: () => {
                         selectVille(point.city);
                       },
                     }}
                   >
                     <LeafletTooltip 
                        direction="top" 
                        className="pm25-map-label"
                        offset={[0, -10]}
                        opacity={1}
                     >
                        {pm25Value} µg/m³
                     </LeafletTooltip>
                     <Popup>
                        <div className="min-w-[160px] p-1 font-sans text-slate-800">
                          <div className="text-lg font-bold mb-1 border-b pb-1">{point.city}</div>
                          
                          <div className="space-y-2 mt-2">
                            <div className="flex flex-col gap-0.5">
                              <span className="text-[10px] font-black text-gray-400 uppercase tracking-wider">{t('map_pollution')}</span>
                              <div className="flex items-center gap-1.5 bg-gray-50 p-1.5 rounded-lg border border-gray-100">
                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }}></div>
                                <span className="text-sm font-bold text-gray-800">
                                  {point.pm25_moyen} <span className="text-[10px] font-normal text-gray-500">µg/m³</span>
                                </span>
                              </div>
                            </div>

                            <div className="flex flex-col gap-0.5">
                              <span className="text-[10px] font-black text-gray-400 uppercase tracking-wider">{t('map_quality')}</span>
                              <div className="flex items-center gap-2">
                                <span 
                                  className="px-2 py-0.5 rounded text-[11px] font-bold text-white uppercase"
                                  style={{ backgroundColor: color }}
                                >
                                  {pm25Label}
                                </span>
                              </div>
                            </div>
                          </div>

                          <button 
                            onClick={() => {
                              selectVille(point.city);
                              router.push("/dashboard/stats");
                            }}
                            className="w-full mt-3 py-2 bg-[#020c18] text-white rounded-xl text-xs font-bold hover:bg-[#00d4b1] transition-colors active:scale-95"
                          >
                            {t('map_view_stats')}
                          </button>
                        </div>
                     </Popup>
                   </CircleMarker>
                 );
               })}
          </LayersControl.Overlay>
        </LayersControl>
      </MapContainer>

      {/* ── Légende cliquable ── */}
      <div className="absolute bottom-6 left-4 z-[1000] space-y-3">
        <div className="glass-card p-4 border-white/10 flex flex-col gap-2.5 min-w-[200px] backdrop-blur-3xl bg-slate-950/80 shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
          <div className="flex flex-col gap-1 mb-1 border-b border-white/5 pb-2">
            <span className="text-[10px] font-black text-[#00d4b1] uppercase tracking-widest flex items-center gap-2">
              <Wind size={14} /> {t('map_pollution') || "Qualité de l'Air"}
            </span>
            <span className="text-[8px] font-bold text-gray-500 uppercase tracking-tighter opacity-50">Standards OMS 2021 · Cliquer pour filtrer</span>
          </div>
          {[
            { key: 'EXCELLENT', color: "#008000", desc: "0–5",    defaultLabel: "Excellent" },
            { key: 'BON',       color: "#4CAF50", desc: "5–15",   defaultLabel: "Bon" },
            { key: 'MODERE',    color: "#FFC107", desc: "15–25",  defaultLabel: "Modéré" },
            { key: 'DEGRADE',   color: "#FF9800", desc: "25–50",  defaultLabel: "Dégradé" },
            { key: 'MAUVAIS',   color: "#FF5722", desc: "50–100", defaultLabel: "Mauvais" },
            { key: 'CRITIQUE',  color: "#B71C1C", desc: ">100",   defaultLabel: "Critique" },
          ].map((item) => {
            const isActive = activeFilter === item.key;
            return (
              <button
                key={item.key}
                onClick={() => setActiveFilter(isActive ? "ALL" : item.key as LevelKey)}
                className={`flex items-center gap-3 group/item w-full text-left rounded-lg px-1.5 py-1 transition-all ${isActive ? "bg-white/10" : "hover:bg-white/5"}`}
              >
                <div className="w-2.5 h-2.5 rounded-full shrink-0 shadow-lg group-hover/item:scale-125 transition-transform" style={{ backgroundColor: item.color, boxShadow: `0 0 10px ${item.color}44` }} />
                <div className="flex justify-between items-center w-full">
                  <span className={`text-[10px] font-black uppercase tracking-tighter leading-none ${isActive ? "text-white" : "text-white/70"}`}>
                    {t(item.key) || item.defaultLabel}
                  </span>
                  <span className="text-[8px] text-gray-500 font-bold tabular-nums">
                    {item.desc} <span className="opacity-50 font-normal">µg/m³</span>
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        .leaflet-container { z-index: 0 !important; }
        .leaflet-popup-content-wrapper { border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }
        .leaflet-control-layers { 
          border-radius: 20px !important; 
          border: none !important; 
          box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
          margin-top: 90px !important;
          margin-right: 20px !important;
        }

        /* Labels PM2.5 sur la carte */
        .leaflet-tooltip-pane .pm25-map-label {
           background: transparent !important;
           border: none !important;
           box-shadow: none !important;
           color: white !important;
           font-weight: 900 !important;
           font-size: 8px !important;
           text-shadow: 0 1px 2px rgba(0,0,0,0.5);
           pointer-events: none;
           padding: 0 !important;
           margin: 0 !important;
           display: flex;
           align-items: center;
           justify-content: center;
        }
        .pm25-map-label:before { display: none !important; }
      `}} />
    </div>
  );
}
