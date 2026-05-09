import apiClient from "./apiClient";

export interface DonutEntry {
  label: string;
  valeur: number;
  couleur: string;
}

export interface ComparaisonAnnuelle {
  annee_courante: number;
  pm25_an_courant: number;
  annee_precedente: number;
  pm25_an_precedent: number;
  evolution_pct: number;
}

export interface ContexteResponse {
  donut_niveaux: DonutEntry[];
  donut_polluants: DonutEntry[];
  comparaison_annuelle: ComparaisonAnnuelle | null;
  uv_ozone: {
    uv_index: number;
    ozone_ppb: number;
    source: string;
  };
}

const contexteService = {
  /**
   * Récupère les données contextuelles (donuts, comparaison annuelle, UV/Ozone).
   * @param city Ville à filtrer (optionnel, null ou "CAMEROON" = données nationales)
   */
  getContexte: async (city?: string | null): Promise<ContexteResponse> => {
    const filter = (city && city !== "CAMEROON") ? `?city=${encodeURIComponent(city)}` : "";
    const response = await apiClient.get(`contexte${filter}`);
    return response.data;
  }
};

export default contexteService;
