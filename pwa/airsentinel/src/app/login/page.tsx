"use client";

import React, { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import authService from "@/services/authService";
import { Mail, Lock, Eye, EyeOff, ArrowLeft, Loader2 } from "lucide-react";
import { notify } from "@/utils/toast";
import { useLanguage } from "@/context/LanguageContext";
import LanguageSwitcher from "@/components/LanguageSwitcher";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const { t } = useLanguage();
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await authService.login({ email, password });
      notify.success(t('login_success'));
      router.push('/dashboard/carte');
    } catch (err: any) {
      console.error("Erreur de connexion:", err);
      notify.error(t('login_error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 sm:p-6 bg-hero-joel overflow-hidden">
      {/* Dark gradient overlay to ensure text readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#020c18]/80 via-[#020c18]/60 to-[#020c18]/90 backdrop-blur-[2px]"></div>

      <div className="relative z-10 w-full max-w-[400px] animate-fade-up my-8">
        {/* Main Glass Card */}
        <div className="glass-card w-full min-h-[550px] pt-8 pb-16 sm:pb-24 px-5 sm:px-8 flex flex-col items-center relative overflow-hidden">

          {/* Back Button */}
          <Link href="/" className="absolute top-6 left-6 text-gray-400 hover:text-white transition-colors z-30">
            <ArrowLeft className="w-6 h-6" />
          </Link>

          <div className="absolute top-6 right-6 z-30">
            <LanguageSwitcher />
          </div>

          {/* Logo - completely inside the card so nothing overflows */}
          <div className="relative w-[100px] h-[100px] mb-4 drop-shadow-[0_0_15px_rgba(0,212,177,0.5)] animate-float flex-shrink-0">
            <Image
              src="/LogoAir.png"
              alt="AirSentinel Logo"
              fill
              className="object-contain"
              priority
            />
          </div>

          {/* Header Text */}
          <div className="text-center w-full mb-6">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              AirSentinel Cameroun
            </h1>
            <p className="text-sm text-gray-300 mt-1">
              {t('hero_title_2')} {t('hero_title_3')}
            </p>
          </div>

          <h2 className="text-[1.35rem] font-medium text-white mb-6">
            {t('login_title')}
          </h2>

          <form className="w-full flex flex-col gap-5 sm:gap-6" onSubmit={handleLogin}>

            {/* Email Field */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] text-gray-300 ml-1">{t('login_email')}</label>
              <div className="relative group">
                <input
                  type="email"
                  autoComplete="email"
                  placeholder={t('login_email_placeholder')}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[3.5rem] text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all"
                  required
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-[var(--teal)]">
                  <Mail className="w-5 h-5 opacity-90 group-focus-within:opacity-100 transition-opacity" />
                </div>
              </div>
            </div>

            {/* Password Field */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[13px] text-gray-300 ml-1">{t('login_password')}</label>
              <div className="relative group">
                <input
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder={t('login_password')}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[5.5rem] text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all mb-1"
                  required
                />
                <div className="absolute inset-y-0 right-0 pr-4 flex items-center gap-2">
                  <Lock className="w-5 h-5 text-[var(--teal)] opacity-90 group-focus-within:opacity-100 transition-opacity pointer-events-none" />
                  <div
                    className="flex items-center text-gray-400 hover:text-white cursor-pointer transition-colors"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                  </div>
                </div>
              </div>
              <div className="w-full flex justify-end">
                <Link href="#" className="text-[12px] text-gray-400 hover:text-[var(--teal)] transition-colors">
                  {t('login_forgot')}
                </Link>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full mt-4 !font-medium flex items-center justify-center gap-2 disabled:opacity-70"
            >
              {isLoading && <Loader2 className="w-5 h-5 animate-spin" />}
              {isLoading ? t('login_processing') : t('login_button')}
            </button>
          </form>

          {/* Footer Text */}
          <div className="mt-20 text-[15px] text-gray-300 text-center">
            {t('login_no_account')}{" "}
            <Link href="/register" className="text-white hover:text-[var(--teal)] font-medium transition-colors">
              {t('login_signup')}
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
