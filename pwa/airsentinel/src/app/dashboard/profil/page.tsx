"use client";

import React, { useState, useEffect } from "react";
import { User, Mail, MapPin, Save, Shield, Bell, BellOff, Loader2, Camera } from "lucide-react";
import authService from "@/services/authService";
import userService from "@/services/userService";
import predictionService from "@/services/predictionService";
import { User as UserType } from "@/types/auth";
import { notify } from "@/utils/toast";
import { useLanguage } from "@/context/LanguageContext";
import { useVille } from "@/context/VilleContext";
import SearchableSelect from "@/components/ui/SearchableSelect";
import { DATASET_CITIES } from "../../../services/dataService";

export default function ProfilPage() {
  const { t } = useLanguage();
  const [user, setUser] = useState<UserType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // Form state
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [city, setCity] = useState("");

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        setFullName(currentUser.full_name || "");
        setEmail(currentUser.email);
        setCity(currentUser.subscribed_city || "");
      } catch (err) {
        notify.error("Impossible de charger votre profil.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchUser();
  }, []);

  const { selectVille } = useVille();

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log("[Profil] Tentative de mise à jour avec:", { fullName, email, city });
    
    if (!fullName || !email) {
      notify.error("Le nom et l'email sont obligatoires.");
      return;
    }

    setIsSaving(true);
    try {
      const updatedUser = await authService.updateProfile({
        full_name: fullName,
        email: email,
        subscribed_city: city
      });
      console.log("[Profil] Mise à jour réussie:", updatedUser);
      setUser(updatedUser);
      // Synchroniser le contexte global de la ville
      if (city) selectVille(city);
      // Notifier la Navbar de mettre à jour les infos utilisateur
      window.dispatchEvent(new Event('userUpdate'));
      notify.success("Profil mis à jour avec succès !");
    } catch (err: any) {
      console.error("[Profil] Erreur lors de la mise à jour:", err);
      notify.error(err.response?.data?.detail || "Erreur lors de la mise à jour.");
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordChange = () => {
    notify.info("Le changement de mot de passe sera disponible dans la prochaine version !");
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const loading = notify.loading("Téléchargement de l'avatar...");
    try {
      const { avatar_url } = await userService.uploadAvatar(file);
      if (user) {
        setUser({ ...user, avatar_url });
      }
      window.dispatchEvent(new Event('userUpdate'));
      notify.dismiss(loading);
      notify.success("Photo de profil mise à jour !");
    } catch (err) {
      notify.dismiss(loading);
      notify.error("Erreur lors de l'envoi de l'image.");
    }
  };

  const toggleAlerts = async () => {
    if (!user) return;
    const newState = !user.is_alerts_enabled;
    try {
      await predictionService.subscribeToCityAlerts(user.subscribed_city || city, newState);
      setUser({ ...user, is_alerts_enabled: newState });
      window.dispatchEvent(new Event('userUpdate'));
      notify.success(newState ? "Alertes activées !" : "Alertes désactivées.");
    } catch (err) {
      notify.error("Erreur lors de la modification des alertes.");
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-12 h-12 text-[var(--teal)] animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-in fade-in duration-700">
      <div className="flex items-center gap-4 mb-8">
        <div className="w-12 h-12 rounded-2xl bg-[var(--teal)]/20 flex items-center justify-center text-[var(--teal)]">
          <User size={28} />
        </div>
        <div>
          <h1 className="text-3xl font-black text-white tracking-tight">Mon Profil</h1>
          <p className="text-gray-400">Gérez vos informations personnelles et vos alertes</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Colonne de gauche : Avatar et Statut d'alerte */}
        <div className="md:col-span-1 space-y-6">
          <div className="glass-card p-6 flex flex-col items-center border-2 border-white/5">
            <div className="relative group mb-6">
              <div className="w-32 h-32 rounded-full border-4 border-[var(--teal)]/30 overflow-hidden bg-slate-800 flex items-center justify-center shadow-2xl group-hover:border-[var(--teal)] transition-all">
                {user?.avatar_url ? (
                  <img src={user.avatar_url} alt="Profile" className="w-full h-full object-cover" />
                ) : (
                  <User size={48} className="text-[var(--teal)]" />
                )}
              </div>
              <button 
                onClick={() => document.getElementById('avatarInput')?.click()}
                className="absolute bottom-0 right-0 p-2.5 bg-[var(--teal)] rounded-xl text-white shadow-xl hover:scale-110 transition-all"
              >
                <Camera size={18} />
              </button>
              <input 
                id="avatarInput"
                type="file" 
                className="hidden" 
                accept="image/*"
                onChange={handleAvatarUpload}
              />
            </div>
            
            <h2 className="text-xl font-bold text-white mb-1 text-center">{user?.full_name}</h2>
            <p className="text-gray-500 text-sm mb-6 text-center">{user?.email}</p>
            
            <div className="w-full pt-6 border-t border-white/5">
              <button 
                onClick={toggleAlerts}
                className={`w-full flex items-center justify-between p-4 rounded-2xl transition-all duration-300 ${
                  user?.is_alerts_enabled 
                  ? "bg-[var(--teal)]/10 text-[var(--teal)] border border-[var(--teal)]/30" 
                  : "bg-white/5 text-gray-500 border border-white/10"
                }`}
              >
                <div className="flex items-center gap-3">
                  {user?.is_alerts_enabled ? <Bell size={20} className="animate-wiggle" /> : <BellOff size={20} />}
                  <span className="font-bold text-sm">Alertes {user?.is_alerts_enabled ? 'actives' : 'inactives'}</span>
                </div>
                <div className={`w-10 h-5 rounded-full relative transition-colors ${user?.is_alerts_enabled ? 'bg-[var(--teal)]' : 'bg-slate-700'}`}>
                  <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${user?.is_alerts_enabled ? 'right-1' : 'left-1'}`} />
                </div>
              </button>
            </div>
          </div>
          
          <div className="glass-card p-5 border border-white/5 bg-slate-900/50">
            <div className="flex items-center gap-3 text-[var(--teal)] mb-3">
              <Shield size={18} />
              <span className="font-bold text-sm uppercase tracking-wider">Sécurité</span>
            </div>
            <p className="text-xs text-gray-400 mb-4 leading-relaxed">
              Vos données sont protégées par un chiffrement de bout en bout conforme aux normes IndabaX.
            </p>
            <button 
              onClick={handlePasswordChange}
              className="text-xs font-bold text-[var(--teal)] hover:underline"
            >
              Changer mon mot de passe
            </button>
          </div>
        </div>

        {/* Colonne de droite : Formulaire */}
        <div className="md:col-span-2">
          <form onSubmit={handleUpdateProfile} className="glass-card p-8 border-2 border-white/5 space-y-8">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase ml-1 flex items-center gap-2">
                  <User size={14} /> Nom Complet
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-[var(--teal)]/50 transition-all"
                  placeholder="Votre nom"
                />
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase ml-1 flex items-center gap-2">
                  <Mail size={14} /> Adresse Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-[var(--teal)]/50 transition-all"
                  placeholder="votre@email.com"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-gray-400 uppercase ml-1 flex items-center gap-2">
                <MapPin size={14} /> Ville par défaut (Alertes)
              </label>
              <SearchableSelect
                options={DATASET_CITIES}
                value={city}
                onChange={setCity}
                label=""
              />
              <p className="text-[11px] text-gray-500 ml-1 italic">
                Cette ville sera utilisée pour vous envoyer des notifications prioritaires en cas de pic de pollution.
              </p>
            </div>

            <div className="pt-4 flex justify-end">
              <button
                type="submit"
                disabled={isSaving}
                className="flex items-center gap-3 bg-[var(--teal)] text-white px-8 py-4 rounded-2xl font-bold hover:shadow-[0_0_30px_rgba(0,212,177,0.4)] hover:scale-105 active:scale-95 transition-all disabled:opacity-50"
              >
                {isSaving ? <Loader2 className="animate-spin" size={20} /> : <Save size={20} />}
                Enregistrer les modifications
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
