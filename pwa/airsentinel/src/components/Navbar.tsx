"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import authService from "../services/authService";
import predictionService from "../services/predictionService";
import { User as UserType } from "../types/auth";
import { User, Home, LogOut, Loader2, Bell, BellOff, Mail, Globe } from "lucide-react";
import { notify } from "@/utils/toast";
import { useLanguage } from "@/context/LanguageContext";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import ThemeToggle from "@/components/ThemeToggle";

export default function Navbar() {
  const { t, lang, setLang } = useLanguage();
  const [currentUser, setCurrentUser] = useState<UserType | null>(null);
  const [originalCity, setOriginalCity] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      if (authService.isAuthenticated()) {
        try {
          const user = await authService.getCurrentUser();
          setCurrentUser(user);
        } catch (err) {
          console.error("Échec de récupération de l'utilisateur:", err);
        }
      }
      setIsLoading(false);
    };
    fetchUser();

    // Écouter les mises à jour de profil pour synchroniser la Navbar
    window.addEventListener('userUpdate', fetchUser);
    return () => window.removeEventListener('userUpdate', fetchUser);
  }, []);

  const handleLogout = () => {
    authService.logout();
    notify.success(t('logout_success'));
    router.push("/login");
  };

  const handleToggleAlerts = async () => {
    if (!currentUser) {
      console.log("[Navbar] Pas d'utilisateur connecté.");
      return;
    }
    
    const targetCity = currentUser.subscribed_city;
    const currentEnabled = currentUser.is_alerts_enabled;
    
    if (!targetCity) {
      notify.error(t('choose_city_error'));
      router.push("/dashboard/profil");
      return;
    }

    try {
      const loading = notify.loading(currentEnabled ? t('disabling') : t('enabling'));
      
      await predictionService.subscribeToCityAlerts(targetCity, !currentEnabled);
      
      // Mettre à jour l'état local
      const updatedUser = { ...currentUser, is_alerts_enabled: !currentEnabled };
      setCurrentUser(updatedUser);
      
      notify.dismiss(loading);
      notify.success(!currentEnabled ? t('alerts_enabled_on').replace('{}', targetCity) : t('alerts_disabled'));
    } catch (err) {
      console.error("[Navbar] Erreur toggle alertes:", err);
      notify.error(t('alerts_error'));
    }
  };

  return (
    <nav
      className="fixed top-0 left-0 right-0 z-[100] px-4 sm:px-8 h-16 flex items-center justify-between border-b border-[var(--border-color)] bg-[var(--bg-primary)]/80 backdrop-blur-xl"
    >
      <div className="flex items-center gap-2.5">
        <Image src="/LogoAir.png" alt="AirSentinel Logo" width={34} height={34} className="drop-shadow-[0_0_10px_rgba(0,212,177,0.3)]" />
        <span className="text-lg font-bold text-[var(--text-primary)] tracking-tight">
          Air<span className="text-[var(--teal)]">Sentinel</span>
        </span>
      </div>

      <div className="flex items-center gap-4 sm:gap-6">
        <Link href="/" className="max-sm:hidden flex items-center gap-1.5 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
          <Home size={16} />
          <span>{t('nav_home')}</span>
        </Link>

        <ThemeToggle />
        <LanguageSwitcher />

        {currentUser && (
          <button
            onClick={handleToggleAlerts}
            className={`
              relative flex items-center gap-2 px-3 h-9 rounded-full border transition-all duration-300 group
              ${currentUser.is_alerts_enabled 
                ? "bg-[var(--teal)]/10 border-[var(--teal)]/40 text-[var(--teal)] shadow-[0_0_15px_rgba(0,212,177,0.2)]" 
                : "bg-[var(--bg-secondary)]/5 border-[var(--border-color)] text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]/10 hover:border-[var(--border-color)]"}
            `}
            title={currentUser.is_alerts_enabled ? `${t('nav_alerts_active')} (${currentUser.subscribed_city})` : t('activate_alerts')}
          >
            {currentUser.is_alerts_enabled ? (
              <>
                <div className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-[var(--teal)] rounded-full animate-pulse shadow-[0_0_8px_rgba(0,212,177,0.8)]" />
                <Bell size={16} className="animate-wiggle" />
                <span className="text-[11px] font-bold tracking-wider max-sm:hidden uppercase">{t('nav_alerts_active')}</span>
              </>
            ) : (
              <>
                <BellOff size={16} />
                <span className="text-[11px] font-medium max-sm:hidden">{t('nav_alerts_off')}</span>
              </>
            )}
          </button>
        )}

        {isLoading ? (
          <Loader2 className="w-5 h-5 text-[var(--teal)] animate-spin" />
        ) : currentUser ? (
          <div className="flex items-center gap-3 pl-4 border-l border-[var(--border-color)]">
            <div className="max-sm:hidden text-right">
              <p className="text-[13px] font-medium text-[var(--text-primary)] leading-tight">
                {currentUser.full_name || t('nav_user_placeholder')}
              </p>
            </div>
            
            <div className="relative group">
              <div 
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="w-9 h-9 rounded-full border-2 border-[var(--teal)]/30 overflow-hidden bg-[var(--bg-primary)] flex items-center justify-center cursor-pointer group-hover:border-[var(--teal)] transition-all"
              >
                {currentUser.avatar_url ? (
                  <Image 
                    src={currentUser.avatar_url} 
                    alt={currentUser.full_name || "User"} 
                    fill 
                    className="object-cover"
                  />
                ) : (
                  <User size={18} className="text-[var(--teal)]" />
                )}
              </div>
              
              {/* Profile Dropdown */}
              <div className={`
                absolute top-12 right-0 bg-[var(--bg-secondary)] border border-[var(--border-color)] p-2 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] whitespace-nowrap min-w-[190px] backdrop-blur-2xl transition-all duration-300
                ${isMenuOpen ? 'opacity-100 visible translate-y-0' : 'opacity-0 invisible translate-y-2 lg:group-hover:opacity-100 lg:group-hover:visible lg:group-hover:translate-y-0'}
              `}>
                <div className="px-3 py-2 border-b border-[var(--border-color)] mb-2">
                  <p className="text-[10px] uppercase tracking-widest text-[var(--text-secondary)] font-bold">{t('account')}</p>
                </div>
                <Link 
                  href="/dashboard/profil"
                  onClick={() => setIsMenuOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-[var(--text-primary)] hover:bg-[var(--teal)]/10 hover:text-[var(--teal)] transition-all mb-1 group/item"
                >
                  <div className="w-8 h-8 rounded-lg bg-[var(--teal)]/10 flex items-center justify-center group-hover/item:bg-[var(--teal)]/20 transition-colors">
                    <User size={16} className="text-[var(--teal)]" />
                  </div>
                  <span className="font-bold">{t('my_profile')}</span>
                </Link>
                <button 
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-rose-400 hover:bg-rose-500/10 transition-all group/logout"
                >
                  <div className="w-8 h-8 rounded-lg bg-rose-500/5 flex items-center justify-center group-hover/logout:bg-rose-500/10 transition-colors">
                    <LogOut size={16} />
                  </div>
                  <span className="font-bold">{t('nav_logout')}</span>
                </button>
              </div>
            </div>
          </div>
        ) : (
          <Link 
            href="/login" 
            className="w-9 h-9 rounded-full bg-[var(--teal)]/10 border border-[var(--teal)]/20 flex items-center justify-center text-[var(--teal)] hover:bg-[var(--teal)]/20 transition-all"
          >
            <User size={18} />
          </Link>
        )}
      </div>
    </nav>
  );
}
