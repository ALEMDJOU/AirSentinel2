"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Map as MapIcon, BarChart2, Brain, HeartPulse } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export default function PWAFooter() {
  const pathname = usePathname();
  const { t } = useLanguage();

  const TABS = [
    { id: "carte",       label: t('footer_carte'),         icon: MapIcon,    href: "/dashboard/carte" },
    { id: "stats",       label: t('footer_stats'),  icon: BarChart2,  href: "/dashboard/stats" },
    { id: "predictions", label: t('footer_predictions'),   icon: Brain,      href: "/dashboard/predictions" },
    { id: "sante",       label: t('footer_sante'),         icon: HeartPulse, href: "/dashboard/sante" },
  ];

  return (
    <div
      className="sm:hidden"
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        background: "var(--bg-primary)",
        opacity: 0.9,
        backdropFilter: "blur(12px)",
        borderTop: "1px solid var(--border-color)",
        padding: "8px 0",
        paddingBottom: "max(8px, env(safe-area-inset-bottom))",
        display: "flex",
        justifyContent: "space-around",
        alignItems: "center",
      }}
    >
      {TABS.map(({ id, label, icon: Icon, href }) => {
        const isActive = pathname === href;
        return (
          <Link
            key={id}
            href={href}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "4px",
              color: isActive ? "var(--teal)" : "var(--text-secondary)",
              textDecoration: "none",
              width: "25%",
              transition: "color 0.2s",
            }}
          >
            <Icon size={22} />
            <span style={{ fontSize: "10px", fontWeight: isActive ? 600 : 500 }}>{label}</span>
          </Link>
        );
      })}
    </div>
  );
}
