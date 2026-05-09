"use client";

import { redirect } from "next/navigation";

export default function DashboardPage() {
  // Par défaut, rediriger vers la carte (comme demandé: "L'écran de démarrage")
  redirect("/dashboard/carte");
}
