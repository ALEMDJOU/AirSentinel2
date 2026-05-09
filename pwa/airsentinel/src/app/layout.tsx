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
import NotificationManager from "@/components/NotificationManager";
import ChatBot from "@/components/ChatBot";
import KeepAlive from "@/components/KeepAlive";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <head />
      <body className={inter.className}>
        <LanguageProvider>
        <Toaster 
          position="top-center"
          toastOptions={{
            duration: 4000,
            style: {
              background: "rgba(15, 23, 42, 0.9)",
              color: "#fff",
              backdropFilter: "blur(10px)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              fontSize: "14px",
              borderRadius: "12px",
            },
          }}
        />
        <KeepAlive />
        <NotificationManager />
        <ChatBot />
        {children}
        </LanguageProvider>
      </body>
    </html>
  );
}
