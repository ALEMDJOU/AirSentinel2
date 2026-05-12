export interface KPIResponse {
  pm25_moyen: number;
  irs_moyen: number | null;
  villes_depassant_oms: number;
  polluant_dominant: string;
  tendance: string;
  total_observations: number;
}

export interface AlerteAnneeLevels {
  FAIBLE: number;
  MODERE: number;
  ELEVE: number;
  CRITIQUE: number;
}

// Format réel de l'API /alertes : { "2022": AlerteAnneeLevels, "2023": ... }
export type AlerteHistorique = Record<string, AlerteAnneeLevels>;
