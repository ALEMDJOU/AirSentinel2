"use client";

import { useEffect } from "react";

/**
 * Composant KeepAlive
 * Envoie une requête légère au backend toutes les 5 minutes pour éviter
 * qu'il ne s'endorme sur Render pendant qu'un utilisateur utilise l'application.
 */
export default function KeepAlive() {
  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://airsentinel-api.onrender.com";
    
    const pingServer = async () => {
      try {
        // On utilise /health car c'est un endpoint léger déjà existant
        await fetch(`${apiUrl}/health`, { 
          method: "GET",
          mode: "no-cors", // On s'en fiche de la réponse, on veut juste toucher le serveur
          cache: "no-store" 
        });
        console.log("Ping de réveil envoyé au backend.");
      } catch (error) {
        // On ignore les erreurs de ping en silence
        console.warn("Échec du ping KeepAlive:", error);
      }
    };

    // Premier ping au chargement
    pingServer();

    // Ping toutes les 5 minutes (300 000 ms)
    const interval = setInterval(pingServer, 300000);

    return () => clearInterval(interval);
  }, []);

  // Ce composant ne rend rien visuellement
  return null;
}
