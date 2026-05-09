import apiClient from "./apiClient";

export interface ProfilRecommandation {
  profil: string;
  icone: string;
  niveau_risque: string;
  couleur: string;
  message: string;
  actions: string[];
}

const healthService = {
  getRealRecommendations: async (ville?: string): Promise<ProfilRecommandation[]> => {
    const params = ville ? { ville } : {};
    const url = "decision/real";
    const response = await apiClient.get(url, { params });
    return response.data;
  }
};

export default healthService;
