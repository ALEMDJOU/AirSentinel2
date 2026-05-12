import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AirSentinel Cameroun — L'IA au service d'un air plus pur",
  description: "Visualisez, Analysez et Anticipez la Qualité de l'Air sur Tout le Territoire Camerounais",
  manifest: "/manifest.json",
  icons: {
    icon: "/LogoAir.png",
    shortcut: "/LogoAir.png",
    apple: "/LogoAir.png",
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "AirSentinel",
  },
  openGraph: {
    title: "AirSentinel Cameroun",
    description: "Plateforme IA de surveillance de la qualité de l'air au Cameroun",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#00d4b1",
  width: "device-width",
  initialScale: 1,
};

import { Toaster } from "react-hot-toast";

import { LanguageProvider } from "@/context/LanguageContext";
import { ThemeProvider } from "@/context/ThemeContext";
import NotificationManager from "@/components/NotificationManager";
import ChatBot from "@/components/ChatBot";
import KeepAlive from "@/components/KeepAlive";
import { VilleProvider } from "@/context/VilleContext";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <head />
      <body className={inter.className}>
        <ThemeProvider>
        <LanguageProvider>
        <VilleProvider>
        <Toaster 
          position="top-center"
          toastOptions={{
            duration: 4000,
            style: {
              background: "var(--bg-secondary)",
              color: "var(--text-primary)",
              backdropFilter: "var(--glass-blur)",
              border: "1px solid var(--border-color)",
              fontSize: "14px",
              borderRadius: "12px",
            },
          }}
        />
        <KeepAlive />
        <NotificationManager />
        <ChatBot />
        {children}
        </VilleProvider>
        </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
