export interface PredictionPoint {
  date: string;
  pm25: number;
  is_prediction?: boolean;
}

export interface MonthlyPM25 {
  annee: number;
  mois: number;
  pm25_moyen: number;
}
