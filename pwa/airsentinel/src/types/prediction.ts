export interface PredictionPoint {
  date: string;
  pm25: number;
  is_prediction?: boolean;
  features?: Record<string, number>; // champs météo/polluants retournés par l'API
}

export interface MonthlyPM25 {
  annee: number;
  mois: number;
  pm25_moyen: number;
}
