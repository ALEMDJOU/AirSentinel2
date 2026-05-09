# 🌍 AirSentinel PWA (Frontend)

Bienvenue dans l'interface de **AirSentinel**, une Progressive Web App (PWA) ultra-moderne développée pour interagir avec le modèle d'Intelligence Artificielle de prédiction de la qualité de l'air au Cameroun.

## ✨ Caractéristiques Principales
- **Tech Stack** : Next.js 15 (App Router), React 19, TypeScript
- **Stylisation** : Tailwind CSS v4, Glassmorphism UI
- **Animations** : Framer Motion
- **Iconographie** : Lucide React
- **Graphiques** : Recharts
- **Cartographie** : Leaflet (React-Leaflet) intégré avec surcouche interactive

## 🚀 Démarrage Rapide

### 1. Prérequis
- **Node.js** (v18+ recommandé)
- **npm** ou **yarn**
- API Backend (FastAPI) en cours d'exécution sur votre machine (port par défaut `8000`).

### 2. Variables d'Environnement
Assurez-vous qu'un fichier `.env.local` est présent à la racine du projet frontend (`pwa/airsentinel/`) avec la configuration adéquate menant à l'API :

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```
> **Note** : Le serveur Next.js en développement requiert `127.0.0.1` à la place de `localhost` pour éviter les soucis de résolution IPv6 vers le backend Python si vous êtes sous Windows/WSL.

### 3. Installation et Exécution
Installez les paquets et lancez le serveur de développement :

```bash
npm install
npm run dev
```

Ensuite, rendez-vous sur : [http://localhost:3000](http://localhost:3000)

## 📁 Architecture du Projet

```text
pwa/airsentinel/
├── public/                 # Images et assets (joel1.jpg, etc.)
├── src/
│   ├── app/                # Next.js App Router (pages: register, dashboard, etc.)
│   ├── components/         # Composants React réutilisables
│   ├── context/            # React Contexts (ex: VilleContext pour le filtre global)
│   ├── services/           # Services Axios pour contacter le backend (API FastAPI)
│   └── types/              # Définitions TypeScript
├── .env.local              # Fichier d'environnement (API URL)
├── next.config.ts          # Configurations avancées Next.js
└── tailwind.config.ts      # Tokens de design de l'application
```

## 🛠️ Modèles de Déploiement

Pour générer un build de production optimisé :

```bash
npm run build
npm start
```
Ce projet est compatible nativement pour un déploiement Vercel, Render ou toute plateforme Node.js standard.
