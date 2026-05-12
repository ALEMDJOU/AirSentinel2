import Navbar from "../../components/Navbar";
import PWAFooter from "../../components/PWAFooter";
import Onboarding from "@/components/Onboarding";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] font-sans transition-colors duration-300">
      <Navbar />
      <Onboarding />
      <div className="pt-[64px] pb-[140px] sm:pb-0">
        {children}
      </div>
      <PWAFooter />
    </div>
  );
}
