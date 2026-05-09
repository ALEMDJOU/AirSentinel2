import apiClient from "./apiClient";
import { VillePoint, CarteAnalyses } from "../types/map";

const mapService = {
  /**
   * Récupère la liste des points géolocalisés (villes) pour la carte.
   */
  async getMapPoints(): Promise<VillePoint[]> {
    const response = await apiClient.get<VillePoint[]>("/carte");
    return response.data;
  },

  /**
   * Récupère les analyses globales enrichies pour la carte et le dashboard.
   * @param city Ville à filtrer (optionnel, null ou "CAMEROON" = données nationales)
   */
  async getMapAnalyses(city?: string | null): Promise<CarteAnalyses> {
    const filter = (city && city !== "CAMEROON") ? `?city=${encodeURIComponent(city)}` : "";
    const response = await apiClient.get<CarteAnalyses>(`/carte/analyses${filter}`);
    return response.data;
  }
};

export default mapService;
