"use client";

import { useEffect } from "react";
import { getMessaging, getToken, onMessage } from "firebase/messaging";
import app from "@/lib/firebase";
import apiClient from "@/services/apiClient";
import authService from "@/services/authService";
import toast from "react-hot-toast";

export default function NotificationManager() {
  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 3;

    const setupNotifications = async () => {
      // Si pas encore connecté, on attend un peu (le temps que le state auth se stabilise)
      if (!authService.isAuthenticated()) {
        if (retryCount < maxRetries) {
          retryCount++;
          setTimeout(setupNotifications, 2000);
        }
        return;
      }

      try {
        console.log("[FCM] Tentative de configuration...");
        // 2. Demander la permission
        const permission = await Notification.requestPermission();
        if (permission !== "granted") {
          console.log("[FCM] Permission refusée.");
          return;
        }

        const messaging = getMessaging(app);
        const token = await getToken(messaging, {
          vapidKey: "BCOhvQLvI5jxno6kfSATjGtotNS-ratoHpGgG0O7lTfmHP_utjn1a2CbgGjOEmmN6o6ZgwfhU0wRtceWfbQ95Lg"
        });

        if (token) {
          console.log("[FCM] Token récupéré:", token);
          await apiClient.post("/notifications/update-token", { fcm_token: token });
          console.log("[FCM] Token synchronisé avec le serveur.");
        }

        onMessage(messaging, (payload) => {
          console.log("[FCM] Message reçu:", payload);
          toast.success(`${payload.notification?.title}: ${payload.notification?.body}`, {
            duration: 8000,
            icon: "🚨",
            style: {
              background: '#1e293b',
              color: '#fff',
              border: '1px solid rgba(0,212,177,0.3)'
            }
          });
        });
      } catch (error) {
        console.error("[FCM] Erreur:", error);
      }
    };

    setupNotifications();
  }, []);

  return null; // Ce composant ne rend rien visuellement
}
