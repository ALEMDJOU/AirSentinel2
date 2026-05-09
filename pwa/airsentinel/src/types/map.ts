export interface VillePoint {
  city: string;
  lat: number | null;
  lon: number | null;
  pm25_moyen: number;
  irs_moyen?: number | null;
  irs_label?: string | null;
  irs_color?: string | null;
}

export interface CarteAnalyses {
  pm25_par_region: Record<string, number>;
  tendance_12_mois: Record<string, number>;
  top_3_polluants: Array<{ polluant: string; moyenne: number }>;
  top_5_villes_critiques: Array<{ city: string; pm25_moyen: number }>;
  episodes_pollution: number;
  pct_depassement_oms: number;
}
