"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

type Language = "fr" | "en";

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  fr: {
    // Navbar
    nav_home: "Accueil",
    nav_alerts_active: "Alertes Actives",
    nav_alerts_off: "Alertes Off",
    nav_logout: "Déconnexion",
    nav_user_placeholder: "Utilisateur",
    nav_login: "Connexion",
    nav_register: "S'inscrire",
    nav_features: "Fonctionnalités",
    
    // Landing - Hero
    hero_title_1: "AirSentinel : ",
    hero_title_2: "L'IA au Service",
    hero_title_3: " d'un Air Plus Pur au Cameroun",
    hero_subtitle: "Visualisez, Analysez et Anticipez la Qualité de l'Air sur Tout le Territoire",
    hero_cta_register: "S'inscrire gratuitement",
    hero_cta_learn: "En savoir plus ↓",
    hero_stat_cities: "Villes",
    hero_stat_regions: "Régions",
    hero_stat_obs: "Observations",
    hero_stat_forecast: "Prédictions",

    // Landing - Pillars
    pillars_title: "Nos Piliers Stratégiques",
    pillar_ai_title: "Anticipation IA",
    pillar_ai_desc: "Prédiction de la concentration PM2.5 à J+1 grâce à un modèle de régression entraîné sur 28 variables météo et historiques. ARIMA par zone pour les tendances à J+3.",
    pillar_map_title: "Cartographie Interactive",
    pillar_map_desc: "Visualisation géospatiale en temps réel de la qualité de l'air dans les 40 grandes villes camerounaises avec l'Indice de Risque Sanitaire (IRS) par zone.",
    pillar_irs_title: "Indice de Risque Sanitaire",
    pillar_irs_desc: "Algorithme exclusif combinant PM2.5, CO, Dust, UV et Ozone via PCA pour calculer un score IRS : Faible · Modéré · Élevé · Critique.",
    pillar_map_real: "CARTE RÉELLE · 10 RÉGIONS",

    // Landing - Tech
    tech_title: "Tech-Stack",
    tech_subtitle: "Des technologies éprouvées pour une performance de production",

    // Landing - Testimonial
    quote_text: "AirSentinel représente une avancée majeure pour la santé publique au Cameroun. Grâce à l'intelligence artificielle, nous pouvons désormais anticiper les épisodes de pollution et protéger les populations les plus vulnérables.",
    quote_author: "FOFACK ALEMDJOU HENRI JOEL",
    quote_role: "4ième année Génie Informatique, ENSPY",

    // Landing - Footer
    footer_rights: "AirSentinel © 2026",
    footer_privacy: "Confidentialité",
    footer_terms: "Conditions",
    footer_partners: "IndabaX Cameroon 2026 · DPA Green Tech · ISSEA · ENSP Yaoundé",
    footer_dates: "17 mars → 7 avril 2026",

    // Auth - Login
    login_title: "Se connecter",
    login_email: "Email",
    login_password: "Mot de passe",
    login_forgot: "Mot de passe oublié?",
    login_no_account: "Pas encore de compte?",
    login_signup: "Inscrivez-vous",
    login_success: "Connexion réussie ! Content de vous revoir.",
    login_error: "Email ou mot de passe incorrect.",
    login_button: "Se connecter",
    login_processing: "Connexion...",

    // Auth - Register
    reg_title: "Créer un compte",
    reg_avatar: "Image de profil",
    reg_fullname: "Nom Complet",
    reg_fullname_placeholder: "Jean Dupont",
    reg_city: "Ville de résidence",
    reg_city_placeholder: "Rechercher votre ville...",
    reg_confirm_pass: "Confirmation du mot de passe",
    reg_confirm_pass_placeholder: "Confirmez le mot de passe",
    reg_button: "Créer mon compte",
    reg_processing: "Création du compte...",
    reg_success: "Compte créé avec succès ! Bienvenue.",
    reg_pass_mismatch: "Les mots de passe ne correspondent pas.",
    reg_have_account: "Déjà un compte?",
    reg_login: "Connectez-vous",
    reg_avatar_uploading: "Envoi de votre photo de profil...",
    reg_avatar_success: "Photo de profil mise à jour.",
    reg_avatar_error: "Profil prêt, mais l'image a échoué : {}",
    
    // PWAFooter
    footer_carte: "Carte",
    footer_stats: "Statistiques",
    footer_predictions: "Prédictions",
    footer_sante: "Santé",

    // CitySelector
    city_search_title: "Recherche Géo-spatiale",
    city_search_placeholder: "Tapez le nom d'une ville (ex: Douala, Yaoundé)...",
    city_national: "National",
    city_all_cameroon: "Tout le Cameroun",
    city_selector_title: "Zone de Surveillance",
    city_selector_desc: "Sélectionnez l'une des 40 villes actives pour l'analyse.",
    city_empty: "Aucun Résultat",
    city_not_found: "La ville \"{}\" n'est pas encore sous surveillance active.",
    city_loading: "Chargement des zones...",

    // Loading
    loading_ai: "Initialisation de l'IA...",
    loading_map: "Chargement de la carte satellitaire...",

    // Predictions Page
    pred_system: "Système Prédictif v4.0",
    pred_lab: "Laboratoire Predictif",
    pred_desc: "Analyse et simulation en temps réel des flux de particules fines.",
    pred_zone: "Zone de Prédiction",
    pred_trend: "Tendance 72h (PM2.5)",
    pred_fluctuation: "Fluctuation",
    pred_after_tomorrow: "Après-Demain",
    pred_in_3_days: "Dans 3 Jours",
    pred_calib: "Analyse de Calibrage",
    pred_calib_desc: "Notre modèle LSTM se recalibre toutes les 6 heures en corrélant les données satellites Copernicus avec les capteurs locaux d'IndabaX.",
    sim_title: "Simulateur Interactif",
    sim_params: "Paramètres Interactifs",
    sim_dust: "Poussière (µg/m³)",
    sim_traffic: "Trafic/CO (ppm)",
    sim_uv: "Indice UV",
    sim_ozone: "Ozone (ppb)",
    sim_temp: "Température (°C)",
    sim_humidity: "Humidité (%)",
    sim_computing: "Recalcul du modèle...",
    sim_result: "Projection PM2.5",
    sim_health: "Impact Santé",

    sim_param_dust: "Indice Poussière",
    sim_param_traffic: "Trafic (CO)",
    sim_param_uv: "Rayonnement UV",
    sim_param_temp: "Température",
    sim_param_hum: "Humidité",
    sim_param_ozone: "Ozone (O3)",
    sim_est_realtime: "Estimation PM2.5 Temps-Réel",
    sim_calc: "Calcul Intelligent...",
    sim_retry: "Réessayer",
    sim_db: "Base de Données",
    sim_ai_precision: "Precision IA",
    sim_lab_control: "AI Lab Control",
    sim_lab_desc: "Simulez l'impact des variables environnementales sur {ville}.",
    today: "Aujourd'hui",
    tomorrow: "Demain",
    after_tomorrow_j2: "Après-demain",

    // Stats Page
    stats_national: "Situation Nationale",
    stats_insights: "Insights: {}",
    stats_change_city: "CHANGER DE VILLE",
    stats_analyse: "Analyse des ",
    stats_data_nat: "Données Nationales",
    stats_data_city: "à {}",
    stats_desc_nat: "Données agrégées en temps réel depuis {x} observations à travers le pays.",
    stats_desc_city: "Données spécifiques à la ville de {y} basées sur {x} observations.",
    stats_no_multi: "Aucune donnée multi-polluants",

    stats_kpi_pm25: "PM2.5 Moyen",
    stats_kpi_oms: "Villes > OMS",
    stats_kpi_pol: "Polluant Majeur",
    stats_kpi_pts: "Points Actifs",
    stats_region_title: "Pollution par Région",
    stats_region_sub: "Répartition géographique de la moyenne PM2.5",
    stats_top5: "Top 5 Villes Critiques",
    stats_alert: "Alerte Santé",
    stats_alert_desc: "Villes avec moyennes > 25 µg/m³. Vigilance recommandée.",
    stats_levels: "Répartition des Niveaux",
    stats_mix: "Mélange de Polluants",
    stats_no_data: "Aucune donnée disponible",
    stats_trend_an: "Tendance Annuelle",
    stats_trend_desc: "Évolution du PM2.5 moyen comparée à l'année précédente.",
    stats_improve: "AMÉLIORATION",
    stats_degrad: "DÉGRADATION",
    stats_analytics: "Analytiques",
    stats_explore_desc: "Explorez les données de qualité de l'air par zone géographique.",

    // Navbar & Notifications
    logout_success: "Déconnexion réussie.",
    choose_city_error: "Veuillez d'abord choisir une ville dans votre profil.",
    disabling: "Désactivation...",
    enabling: "Activation des alertes...",
    alerts_enabled_on: "Alertes activées sur {} !",
    alerts_disabled: "Alertes désactivées.",
    alerts_error: "Impossible de modifier vos alertes.",
    activate_alerts: "Activer les alertes",
    account: "Compte",
    my_profile: "Mon Profil",

    // Sante Page
    health_title_1: "Santé & ",
    health_title_2: "Protection",
    health_sub_city_selected: "Choisissez un profil pour voir les recommandations.",
    health_sub_no_city: "Sélectionnez votre ville pour commencer.",
    health_dash_link: "Tableau de bord",
    health_change_city: "Changer de ville",
    health_where_are_you: "Où êtes-vous ?",
    health_where_desc: "La qualité de l'air varie selon votre position. Sélectionnez une ville pour accéder aux conseils santé adaptés.",
    health_select_city: "Sélectionner une ville...",
    
    // Profiles
    health_all_profiles: "Tous les profils",
    health_prof_children: "Enfants",
    health_prof_adults: "Adultes",
    health_prof_seniors: "Seniors",
    health_prof_asthma: "Asthmatiques",
    health_desc_children: "Préconisations pour les enfants (< 12 ans)",
    health_desc_adults: "Préconisations pour les adultes",
    health_desc_seniors: "Préconisations pour les personnes âgées",
    health_desc_asthma: "Préconisations pour les asthmatiques",
    health_view_tips: "Voir les conseils",
    health_switch_to: "Passer à :",
    health_reset: "Réinitialiser",
    health_ai_note: "Note IA : Ces recommandations sont basées sur les normes de l'OMS et adaptées à chaque profil. Si vous ressentez des difficultés respiratoires persistantes, contactez immédiatement les services de santé de votre district.",
    
    // Sub pages common
    health_city_choose: "Choisissez la ville",
    health_req_city: "Sélectionnez une ville pour obtenir les recommandations pour les {}.",
    health_alert_pollution: "ALERTE : POLLUTION {}",
    health_level: "Niveau {}",
    health_ventilation: "Ventilation",
    health_sport: "Sport",
    health_outdoors: "Sortie",
    health_mask: "Masque",
    health_opt_optimal: "Optimale",
    health_opt_limited: "Limitée",
    health_opt_advise: "Conseillé",
    health_opt_caution: "Prudence",
    health_opt_possible: "Possible",
    health_opt_limit: "Limiter",
    health_opt_no: "Non",
    health_opt_yes: "Oui",
    health_alert_msg: "Message d'alerte",
    health_loading: "Chargement...",
    health_priority_actions: "Actions prioritaires",
    health_attention: "Attention",
    health_continue_explore: "Continuer l'exploration",
    health_discover_other: "Découvrez les recommandations pour les autres profils",

    health_title: "Impact Sanitaire",
    health_desc: "Analyse de l'impact de la qualité de l'air sur la santé publique.",
    health_risk: "Niveau de Risque",
    health_reco: "Recommandations Médicales",
    health_sensible: "Personnes Sensibles",
    health_general: "Population Générale",

    // General
    error_load: "Impossible de charger les données.",
    back: "Retour",

    // SearchableSelect
    search_city: "Rechercher une ville...",
    select_city: "Sélectionnez votre ville",
    no_city_found: "Aucune ville trouvée",

    // LeafletMap
    map_search_placeholder: "Rechercher une ville...",
    map_sync: "Synchronisation des stations...",
    map_plan: "🗺️ Plan (OSM)",
    map_sat: "📡 Satellite",
    map_heatmap: "🔥 Heatmap",
    map_stations: "📍 Stations",
    map_quality: "Qualité de l'air",
    map_pollution: "Pollution PM2.5",
    map_view_stats: "Voir les statistiques",
    map_geo_unsupported: "La géolocalisation n'est pas supportée par votre navigateur.",
    map_geo_error: "Impossible d'accéder à votre position.",
    level_good: "Bon",
    level_mod: "Modéré",
    level_high: "Élevé",
    level_crit: "Critique",
    oms_thresholds: "Concentration µg/m³ (seuils OMS)",

    // ChatBot
    bot_welcome: "Bonjour ! Je suis **SentinelIA**. Comment puis-je vous aider aujourd'hui ?",
    bot_error: "Désolé, une erreur est survenue. Veuillez réessayer.",
    bot_reset_msg: "Conversation réinitialisée. Comment puis-je vous aider ?",
    bot_online: "En ligne",
    bot_reset: "Réinitialiser",
    bot_placeholder: "Message à SentinelIA...",
    bot_mistakes: "SentinelIA peut faire des erreurs.",
    sug_irs: "C'est quoi l'IRS ?",
    sug_harmattan: "Conseils pour l'Harmattan ?",
    sug_alerts: "Pourquoi activer les alertes ?",

    // Auth Pages
    reg_personal_info: "Informations Personnelles",
    reg_security_profil: "Sécurité & Profil",
    reg_next: "Suivant",
    reg_back: "Retour",
    reg_fill_fields: "Veuillez remplir tous les champs obligatoires.",
    login_email_placeholder: "votre@email.com",
  },
  en: {
    // Navbar
    nav_home: "Home",
    nav_alerts_active: "Alerts On",
    nav_alerts_off: "Alerts Off",
    nav_activate_alerts: "Activate mail alerts",
    nav_logout: "Logout",
    nav_user_placeholder: "User",
    nav_login: "Login",
    nav_register: "Register",
    nav_features: "Features",

    // Landing - Hero
    hero_title_1: "AirSentinel: ",
    hero_title_2: "AI at the Service",
    hero_title_3: " of Purer Air in Cameroon",
    hero_subtitle: "Visualize, Analyze and Anticipate Air Quality Across the Territory",
    hero_cta_register: "Sign up for free",
    hero_cta_learn: "Learn more ↓",
    hero_stat_cities: "Cities",
    hero_stat_regions: "Regions",
    hero_stat_obs: "Observations",
    hero_stat_forecast: "Forecasts",

    // Landing - Pillars
    pillars_title: "Our Strategic Pillars",
    pillar_ai_title: "AI Anticipation",
    pillar_ai_desc: "Prediction of PM2.5 concentration at D+1 using a regression model trained on 28 weather and historical variables. ARIMA per zone for trends at D+3.",
    pillar_map_title: "Interactive Mapping",
    pillar_map_desc: "Real-time geospatial visualization of air quality in 40 major Cameroonian cities with the Health Risk Index (HRI) per zone.",
    pillar_irs_title: "Health Risk Index",
    pillar_irs_desc: "Exclusive algorithm combining PM2.5, CO, Dust, UV, and Ozone via PCA to calculates an HRI score: Low · Moderate · High · Critical.",
    pillar_map_real: "REAL MAP · 10 REGIONS",

    // Landing - Tech
    tech_title: "Tech-Stack",
    tech_subtitle: "Proven technologies for production performance",

    // Landing - Testimonial
    quote_text: "AirSentinel represents a major breakthrough for public health in Cameroon. Thanks to artificial intelligence, we can now anticipate pollution events and protect the most vulnerable populations.",
    quote_author: "FOFACK ALEMDJOU HENRI JOEL",
    quote_role: "4th year Computer Engineering, ENSPY",

    // Landing - Footer
    footer_rights: "AirSentinel © 2026",
    footer_privacy: "Privacy",
    footer_terms: "Terms",
    footer_partners: "IndabaX Cameroon 2026 · DPA Green Tech · ISSEA · ENSP Yaounde",
    footer_dates: "March 17 → April 7, 2026",

    // Auth - Login
    login_title: "Login",
    login_email: "Email",
    login_password: "Password",
    login_forgot: "Forgot password?",
    login_no_account: "Don't have an account?",
    login_signup: "Sign up",
    login_success: "Login successful! Good to see you again.",
    login_error: "Incorrect email or password.",
    login_button: "Login",
    login_processing: "Logging in...",

    // Auth - Register
    reg_title: "Create an account",
    reg_avatar: "Profile Image",
    reg_fullname: "Full Name",
    reg_fullname_placeholder: "John Doe",
    reg_city: "City of residence",
    reg_city_placeholder: "Search your city...",
    reg_confirm_pass: "Confirm password",
    reg_confirm_pass_placeholder: "Confirm your password",
    reg_button: "Create my account",
    reg_processing: "Creating account...",
    reg_success: "Account created successfully! Welcome.",
    reg_pass_mismatch: "Passwords do not match.",
    reg_have_account: "Already have an account?",
    reg_login: "Login here",
    reg_avatar_uploading: "Sending your profile picture...",
    reg_avatar_success: "Profile picture updated.",
    reg_avatar_error: "Profile ready, but image failed: {}",

    // PWAFooter
    footer_carte: "Map",
    footer_stats: "Analytics",
    footer_predictions: "AI Forecast",
    footer_sante: "Health",

    // CitySelector
    city_search_title: "Geospatial Search",
    city_search_placeholder: "Type a city name (e.g., Douala, Yaounde)...",
    city_national: "National",
    city_all_cameroon: "All Cameroon",
    city_selector_title: "Monitoring Zone",
    city_selector_desc: "Select one of the 40 active cities for analysis.",
    city_empty: "No Results",
    city_not_found: "The city \"{}\" is not currently under active surveillance.",
    city_loading: "Loading zones...",

    // Loading
    loading_ai: "Initializing AI Engine...",
    loading_map: "Loading satellite map...",

    // Predictions Page
    pred_system: "Predictive System v4.0",
    pred_lab: "Predictive AI Lab",
    pred_desc: "Real-time analysis and simulation of fine particulate matter.",
    pred_zone: "Prediction Zone",
    pred_trend: "72h Trend (PM2.5)",
    pred_fluctuation: "Fluctuation",
    pred_after_tomorrow: "Day After Tomorrow",
    pred_in_3_days: "In 3 Days",
    pred_calib: "Calibration Analysis",
    pred_calib_desc: "Our LSTM model recalibrates every 6 hours by correlating Copernicus satellite data with local IndabaX sensors.",
    sim_title: "Interactive Simulator",
    sim_params: "Environment Parameters",
    sim_dust: "Dust (µg/m³)",
    sim_traffic: "Traffic/CO (ppm)",
    sim_uv: "UV Index",
    sim_ozone: "Ozone (ppb)",
    sim_temp: "Temperature (°C)",
    sim_humidity: "Humidity (%)",
    sim_computing: "Recalculating ML model...",
    sim_result: "Projected PM2.5",
    sim_health: "Health Impact",

    sim_param_dust: "Dust Index",
    sim_param_traffic: "Traffic (CO)",
    sim_param_uv: "UV Radiation",
    sim_param_temp: "Temperature",
    sim_param_hum: "Humidity",
    sim_param_ozone: "Ozone (O3)",
    sim_est_realtime: "Real-Time PM2.5 Estimation",
    sim_calc: "Smart Computing...",
    sim_retry: "Retry",
    sim_db: "Database",
    sim_ai_precision: "AI Precision",
    sim_lab_control: "AI Lab Control",
    sim_lab_desc: "Simulate the impact of environmental variables on {ville}.",
    today: "Today",
    tomorrow: "Tomorrow",
    after_tomorrow_j2: "After tomorrow",
    // Stats Page
    stats_national: "National Overview",
    stats_insights: "Insights: {}",
    stats_change_city: "CHANGE CITY",
    stats_analyse: "Analysis of ",
    stats_data_nat: "National Data",
    stats_data_city: "in {}",
    stats_desc_nat: "Real-time aggregated data from {x} observations across the country.",
    stats_desc_city: "Specific data for the city of {y} based on {x} observations.",
    stats_no_multi: "No multi-pollutant data",

    stats_kpi_pm25: "Avg PM2.5",
    stats_kpi_oms: "Cities > WHO",
    stats_kpi_pol: "Top Pollutant",
    stats_kpi_pts: "Active Sensors",
    stats_region_title: "Regional Pollution",
    stats_region_sub: "Geographic distribution of average PM2.5",
    stats_top5: "Top 5 Critical Cities",
    stats_alert: "Health Alert",
    stats_alert_desc: "Cities with averages > 25 µg/m³. Vigilance recommended.",
    stats_levels: "Level Distribution",
    stats_mix: "Pollutants Mix",
    stats_no_data: "No data available",
    stats_trend_an: "Yearly Trend",
    stats_trend_desc: "Evolution of average PM2.5 compared to previous year.",
    stats_improve: "IMPROVEMENT",
    stats_degrad: "DEGRADATION",
    stats_analytics: "Analytics",
    stats_explore_desc: "Explore air quality data by geographical area.",

    // Navbar & Notifications
    logout_success: "Logout successful.",
    choose_city_error: "Please choose a city in your profile first.",
    disabling: "Disabling...",
    enabling: "Enabling alerts...",
    alerts_enabled_on: "Alerts enabled on {} !",
    alerts_disabled: "Alerts disabled.",
    alerts_error: "Unable to modify your alerts.",
    activate_alerts: "Activate alerts",
    account: "Account",
    my_profile: "My Profile",

    // Sante Page
    health_title_1: "Health & ",
    health_title_2: "Protection",
    health_sub_city_selected: "Choose a profile to see recommendations.",
    health_sub_no_city: "Select your city to start.",
    health_dash_link: "Dashboard",
    health_change_city: "Change city",
    health_where_are_you: "Where are you?",
    health_where_desc: "Air quality varies by location. Select a city to access tailored health advice.",
    health_select_city: "Select a city...",
    
    // Profiles
    health_all_profiles: "All profiles",
    health_prof_children: "Children",
    health_prof_adults: "Adults",
    health_prof_seniors: "Seniors",
    health_prof_asthma: "Asthmatics",
    health_desc_children: "Recommendations for children (< 12 years)",
    health_desc_adults: "Recommendations for adults",
    health_desc_seniors: "Recommendations for the elderly",
    health_desc_asthma: "Recommendations for asthmatics",
    health_view_tips: "View tips",
    health_switch_to: "Switch to:",
    health_reset: "Reset",
    health_ai_note: "AI Note : These recommendations are based on WHO standards and tailored to each profile. If you experience persistent breathing difficulties, contact your local health services immediately.",

    // Sub pages common
    health_city_choose: "Choose city",
    health_req_city: "Select a city to get recommendations for {}.",
    health_alert_pollution: "ALERT: {} POLLUTION",
    health_level: "Level {}",
    health_ventilation: "Ventilation",
    health_sport: "Sport",
    health_outdoors: "Outdoors",
    health_mask: "Mask",
    health_opt_optimal: "Optimal",
    health_opt_limited: "Limited",
    health_opt_advise: "Advised",
    health_opt_caution: "Caution",
    health_opt_possible: "Possible",
    health_opt_limit: "Limit",
    health_opt_no: "No",
    health_opt_yes: "Yes",
    health_alert_msg: "Alert Message",
    health_loading: "Loading...",
    health_priority_actions: "Priority Actions",
    health_attention: "Attention",
    health_continue_explore: "Continue Exploring",
    health_discover_other: "Discover recommendations for other profiles",

    health_title: "Health Impact",
    health_desc: "Analysis of air quality impact on public health.",
    health_risk: "Risk Level",
    health_reco: "Medical Recommendations",
    health_sensible: "Sensitive Groups",
    health_general: "General Public",

    // General
    error_load: "Unable to fetch data.",
    back: "Back",

    // SearchableSelect
    search_city: "Search for a city...",
    select_city: "Select your city",
    no_city_found: "No city found",

    // LeafletMap
    map_search_placeholder: "Search for a city...",
    map_sync: "Syncing stations...",
    map_plan: "🗺️ Map (OSM)",
    map_sat: "📡 Satellite",
    map_heatmap: "🔥 Heatmap",
    map_stations: "📍 Stations",
    map_quality: "Air Quality",
    map_pollution: "PM2.5 Pollution",
    map_view_stats: "View Statistics",
    map_geo_unsupported: "Geolocation is not supported by your browser.",
    map_geo_error: "Unable to access your location.",
    level_good: "Good",
    level_mod: "Moderate",
    level_high: "High",
    level_crit: "Critical",
    oms_thresholds: "PM2.5 Concentration (WHO thresholds)",

    // ChatBot
    bot_welcome: "Hello! I am **SentinelIA**. How can I help you today?",
    bot_error: "Sorry, an error occurred. Please try again.",
    bot_reset_msg: "Conversation reset. How can I help you?",
    bot_online: "Online",
    bot_reset: "Reset",
    bot_placeholder: "Message SentinelIA...",
    bot_mistakes: "SentinelIA can make mistakes.",
    sug_irs: "What is HRI?",
    sug_harmattan: "Tips for Harmattan?",
    sug_alerts: "Why enable alerts?",

    // Auth Pages
    reg_personal_info: "Personal Information",
    reg_security_profil: "Security & Profile",
    reg_next: "Next",
    reg_back: "Back",
    reg_fill_fields: "Please fill in all required fields.",
    login_email_placeholder: "your@email.com",
  }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Language>("fr");

  // Charger la préférence au montage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("app_lang") as Language;
      if (stored === "fr" || stored === "en") {
        setLang(stored);
      }
    }
  }, []);

  // Sauvegarder la préférence
  const handleSetLang = (newLang: Language) => {
    setLang(newLang);
    if (typeof window !== "undefined") {
      localStorage.setItem("app_lang", newLang);
    }
  };

  const t = React.useCallback((key: string) => {
    return translations[lang][key] || key;
  }, [lang]);

  return (
    <LanguageContext.Provider value={{ lang, setLang: handleSetLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
