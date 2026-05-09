import apiClient from "./apiClient";
import { KPIResponse, AlerteHistorique } from "../types/pollution";

const kpiService = {
  getNationalKPIs: async (city?: string | null): Promise<KPIResponse> => {
    // Si la ville est "CAMEROON" ou nulle, on ne filtre pas (données nationales)
    const filter = (city && city !== "CAMEROON") ? `?city=${encodeURIComponent(city)}` : "";
    const response = await apiClient.get(`kpis${filter}`);
    return response.data;
  },

  getAlertesHistorique: async (): Promise<AlerteHistorique[]> => {
    const response = await apiClient.get("alertes");
    return response.data;
  }
};

export default kpiService;
