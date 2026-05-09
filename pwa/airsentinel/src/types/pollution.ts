export interface KPIResponse {
  pm25_moyen: number;
  irs_moyen: number | null;
  villes_depassant_oms: number;
  polluant_dominant: string;
  tendance: string;
  total_observations: number;
}

export interface AlerteHistorique {
  niveau: string;
  count: number;
  color: string;
}
