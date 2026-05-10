import Navbar from "../../components/Navbar";
import PWAFooter from "../../components/PWAFooter";
import Onboarding from "@/components/Onboarding";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#020c18] text-[#e0f2fe] font-sans">
      <Navbar />
      <Onboarding />
      <div className="pt-[64px] pb-[140px] sm:pb-0">
        {children}
      </div>
      <PWAFooter />
    </div>
  );
}
