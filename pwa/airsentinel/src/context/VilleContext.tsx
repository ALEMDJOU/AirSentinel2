"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import authService from "@/services/authService";

interface VilleContextType {
  ville: string | null;
  setVille: (ville: string | null) => void;
  selectVille: (ville: string) => void;
}

const VilleContext = createContext<VilleContextType | undefined>(undefined);

export function VilleProvider({ children }: { children: ReactNode }) {
  const [ville, setVille] = useState<string | null>(null);

  useEffect(() => {
    const initVille = async () => {
      if (authService.isAuthenticated()) {
        try {
          const user = await authService.getCurrentUser();
          if (user && user.subscribed_city) {
            setVille(user.subscribed_city);
          }
        } catch (err) {
          console.error("Erreur init ville context:", err);
        }
      }
    };
    initVille();
  }, []);

  const selectVille = (newVille: string) => {
    setVille(newVille);
  };

  return (
    <VilleContext.Provider value={{ ville, setVille, selectVille }}>
      {children}
    </VilleContext.Provider>
  );
}

export function useVille() {
  const context = useContext(VilleContext);
  if (!context) {
    throw new Error("useVille must be used within a VilleProvider");
  }
  return context;
}
