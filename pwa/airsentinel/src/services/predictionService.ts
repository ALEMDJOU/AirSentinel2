import apiClient from "./apiClient";
import { PredictionPoint, MonthlyPM25 } from "../types/prediction";

const predictionService = {
  getShortTerm: async (city?: string | null): Promise<PredictionPoint[]> => {
    // Si la ville n'est pas spécifiée, on ne peut pas prédire
    if (!city || city === "CAMEROON") {
       throw new Error("Veuillez sélectionner une ville pour voir les prédictions.");
    }
    const response = await apiClient.get(`predictions/short-term?city=${encodeURIComponent(city)}`);
    return response.data;
  },

  getMonthly: async (): Promise<MonthlyPM25[]> => {
    const response = await apiClient.get("predictions/monthly");
    return response.data;
  },

  computeInteractive: async (city: string, features: Record<string, number>) => {
    try {
      const response = await apiClient.post("predictions/compute", { city: city, features });
      return response.data;
    } catch (err: any) {
      console.error("[AI Lab] Computation failed:", err);
      throw err;
    }
  },

  subscribeToCityAlerts: async (city: string, isEnabled: boolean = true) => {
    try {
      const response = await apiClient.put("users/me/subscription", { 
        subscribed_city: city,
        is_alerts_enabled: isEnabled
      });
      return response.data;
    } catch (err: any) {
      console.error("[Alerts] Subscription failed:", err.message);
      throw err;
    }
  }
};

export default predictionService;
