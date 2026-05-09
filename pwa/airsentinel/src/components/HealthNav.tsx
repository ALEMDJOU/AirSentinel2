"use client";

import { MapPin, ChevronDown, ArrowLeft, User, Baby, UserCog, Wind } from "lucide-react";
import { useVille } from "@/context/VilleContext";
import { useLanguage } from "@/context/LanguageContext";
import { useState } from "react";
import { useRouter } from "next/navigation";

interface HealthNavProps {
  currentPage: "enfants" | "adultes" | "personnes-agees" | "asmatiques";
}

export default function HealthNav({ currentPage }: HealthNavProps) {
  const { ville, selectVille } = useVille();
  const { t } = useLanguage();
  const router = useRouter();
  const [showDropdown, setShowDropdown] = useState(false);

  const pages = [
    { id: "enfants" as const, label: t('health_prof_children'), icon: Baby, href: "/dashboard/sante/enfants" },
    { id: "adultes" as const, label: t('health_prof_adults'), icon: User, href: "/dashboard/sante/adultes" },
    { id: "personnes-agees" as const, label: t('health_prof_seniors'), icon: UserCog, href: "/dashboard/sante/personnes-agees" },
    { id: "asmatiques" as const, label: t('health_prof_asthma'), icon: Wind, href: "/dashboard/sante/asmatiques" },
  ];

  const handleSelectPage = (href: string) => {
    router.push(href);
  };

  return (
    <div className="flex flex-wrap items-center gap-3 mb-6">
      <button
        onClick={() => router.push("/dashboard/sante")}
        className="group flex items-center gap-3 px-5 py-2.5 bg-slate-900/60 backdrop-blur-md border border-white/20 rounded-2xl text-white hover:border-[#00d4b1]/50 hover:bg-[#00d4b1]/5 transition-all active:scale-95 shadow-lg shrink-0"
      >
        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform text-[#00d4b1]" />
        <span className="font-black text-[11px] uppercase tracking-widest">{t('health_all_profiles')}</span>
      </button>

      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-2 px-4 py-2.5 bg-[#00d4b1]/10 border border-[#00d4b1]/50 rounded-2xl text-[#00d4b1] shadow-[0_0_20px_rgba(0,212,177,0.1)]">
          {pages.find(p => p.id === currentPage)?.icon && (() => {
            const Icon = pages.find(p => p.id === currentPage)!.icon;
            return <Icon size={18} />;
          })()}
          <span className="font-black text-[11px] uppercase tracking-widest leading-none">
            {pages.find(p => p.id === currentPage)?.label}
          </span>
        </div>

        <div className="w-px h-8 bg-white/10 mx-2 hidden sm:block" />

        <div className="flex items-center gap-2">
          {pages.filter(p => p.id !== currentPage).map((page) => {
            const Icon = page.icon;
            return (
              <button
                key={page.id}
                onClick={() => handleSelectPage(page.href)}
                className="group flex items-center gap-2 px-3 py-2 bg-slate-900/60 border border-white/10 rounded-2xl text-white/70 hover:text-white hover:border-[#00d4b1]/50 hover:bg-[#00d4b1]/10 transition-all active:scale-95 shadow-lg"
                title={`${t('health_switch_to')} ${page.label}`}
              >
                <Icon size={18} className="group-hover:scale-110 transition-transform" />
                <span className="font-bold text-[10px] uppercase tracking-wider hidden md:block">{page.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="relative">
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          className="flex items-center gap-3 px-5 py-2.5 bg-[#00d4b1] border border-white/20 rounded-2xl text-white shadow-[0_4px_20px_rgba(0,212,177,0.3)] hover:bg-[#00b89c] hover:scale-105 transition-all active:scale-95 shrink-0"
        >
          <MapPin size={18} fill="white" />
          <span className="font-black text-[11px] uppercase tracking-widest max-w-[120px] truncate">{ville || t('health_change_city')}</span>
          <ChevronDown size={18} className={`transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
        </button>

        {showDropdown && (
          <div className="absolute top-full right-0 mt-2 bg-[#020c18] border border-white/10 rounded-2xl shadow-2xl overflow-hidden max-h-[250px] overflow-y-auto z-50 min-w-[180px]">
            <button
              onClick={() => { selectVille(""); setShowDropdown(false); }}
              className="w-full text-left px-4 py-3 hover:bg-red-500/20 text-red-400 font-medium transition-colors border-b border-white/5"
            >
              {t('health_reset')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
