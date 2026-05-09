"use client";
import React, { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import authService from "@/services/authService";
import userService from "@/services/userService";
import SearchableSelect from "@/components/ui/SearchableSelect";
import { Mail, Lock, Eye, EyeOff, ArrowLeft, Image as ImageIcon, User, Loader2, MapPin } from "lucide-react";
import { notify } from "@/utils/toast";
import { useLanguage } from "@/context/LanguageContext";
import LanguageSwitcher from "@/components/LanguageSwitcher";

import { DATASET_CITIES } from "@/services/dataService";

export default function RegisterPage() {
  const [step, setStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [city, setCity] = useState("Douala");
  const [avatar, setAvatar] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { t, lang } = useLanguage();

  const router = useRouter();

  const handleNextStep = (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName || !email || !city) {
      notify.error(t('reg_fill_fields'));
      return;
    }
    setStep(2);
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    if (password !== confirmPassword) {
      notify.error(t('reg_pass_mismatch'));
      setIsLoading(false);
      return;
    }

    try {
      // 1. Inscription + Connexion (récupère le token direct)
      await authService.register({
        email,
        full_name: fullName,
        password,
        subscribed_city: city
      });

      notify.success(t('reg_success'));

      // 2. Upload de l'avatar si présent
      if (avatar) {
        const loadingToast = notify.loading(t('reg_avatar_uploading'));
        try {
          await userService.uploadAvatar(avatar);
          notify.dismiss(loadingToast);
          notify.success(t('reg_avatar_success'));
        } catch (avatarErr: any) {
          notify.dismiss(loadingToast);
          console.error("Erreur lors de l'upload de l'avatar:", avatarErr);
          const detail = avatarErr.response?.data?.detail || "Vérifiez vos paramètres Supabase.";
          notify.error(t('reg_avatar_error').replace('{}', detail));
        }
      }

      // 3. Redirection vers la carte
      router.push('/dashboard/carte');
    } catch (err: any) {
      console.error("Erreur d'inscription:", err);
      const detail = err.response?.data?.detail || t('error_load');
      notify.error(detail);
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
        <div className="glass-card w-full pt-8 pb-16 sm:pb-24 px-5 sm:px-8 flex flex-col items-center relative overflow-hidden">

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

          {/* Progress Indicator */}
          <div className="flex items-center gap-2 mb-6 w-full max-w-[120px]">
            <div className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${step >= 1 ? 'bg-[var(--teal)]' : 'bg-white/10'}`}></div>
            <div className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${step >= 2 ? 'bg-[var(--teal)]' : 'bg-white/10'}`}></div>
          </div>

          <h2 className="text-[1.35rem] font-medium text-white mb-6">
            {step === 1 ? t('reg_personal_info') : t('reg_security_profil')}
          </h2>

          <form className="w-full flex flex-col gap-5 sm:gap-6" onSubmit={step === 1 ? handleNextStep : handleRegister}>
            
            {step === 1 && (
              <div className="flex flex-col gap-5 sm:gap-6 animate-fade-in">
                {/* Full Name Field */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[13px] text-gray-300 ml-1">{t('reg_fullname')}</label>
                  <div className="relative group">
                    <input
                      type="text"
                      placeholder={t('reg_fullname_placeholder')}
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[3.5rem] text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all"
                      required
                    />
                    <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-[var(--teal)]">
                      <User className="w-5 h-5 opacity-90 group-focus-within:opacity-100 transition-opacity" />
                    </div>
                  </div>
                </div>

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

                {/* City Field (Smart Selector) */}
                <SearchableSelect
                  label={t('reg_city')}
                  options={DATASET_CITIES}
                  value={city}
                  onChange={(val) => setCity(val)}
                  placeholder={t('reg_city_placeholder')}
                />

                {/* Next Step Button */}
                <button
                  type="submit"
                  className="btn-primary w-full mt-4 !font-medium flex items-center justify-center gap-2"
                >
                  {t('reg_next')}
                </button>
              </div>
            )}

            {step === 2 && (
              <div className="flex flex-col gap-5 sm:gap-6 animate-fade-in">
                {/* Profile Image Field */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[13px] text-gray-300 ml-1">{t('reg_avatar')}</label>
                  <div className="relative group">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => setAvatar(e.target.files?.[0] || null)}
                      className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[3.5rem] file:mr-4 file:h-full file:px-3 file:border-0 file:text-[11px] file:font-semibold file:bg-[var(--teal)] file:text-[#020c18] hover:file:bg-[#00b396] text-white text-sm focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all cursor-pointer overflow-hidden flex items-center"
                    />
                    <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-[var(--teal)]">
                      <ImageIcon className="w-5 h-5 opacity-90 group-focus-within:opacity-100 transition-opacity" />
                    </div>
                  </div>
                </div>

                {/* Password Field */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[13px] text-gray-300 ml-1">{t('login_password')}</label>
                  <div className="relative group">
                    <input
                      type={showPassword ? "text" : "password"}
                      autoComplete="new-password"
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
                </div>

                {/* Confirm Password Field */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[13px] text-gray-300 ml-1">{t('reg_confirm_pass')}</label>
                  <div className="relative group">
                    <input
                      type={showPassword ? "text" : "password"}
                      autoComplete="new-password"
                      placeholder={t('reg_confirm_pass_placeholder')}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full h-[1.1cm] bg-[#1e293b]/40 border border-white/10 rounded-xl pl-4 pr-[5.5rem] text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]/50 transition-all"
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
                </div>

                <div className="flex gap-4 mt-4">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="flex-1 h-[1.1cm] bg-white/5 border border-white/10 rounded-xl text-white font-medium hover:bg-white/10 transition-all"
                  >
                    {t('reg_back')}
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="flex-[2] btn-primary !mt-0 !font-medium flex items-center justify-center gap-2 disabled:opacity-70"
                  >
                    {isLoading && <Loader2 className="w-5 h-5 animate-spin" />}
                    {isLoading ? t('reg_processing') : t('reg_button')}
                  </button>
                </div>
              </div>
            )}
          </form>

          {/* Footer Text */}
          <div className="mt-20 text-[15px] text-gray-300 text-center">
            {t('reg_have_account')}{" "}
            <Link href="/login" className="text-white hover:text-[var(--teal)] font-medium transition-colors">
              {t('reg_login')}
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
