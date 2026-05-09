import Navbar from "../../components/Navbar";
import PWAFooter from "../../components/PWAFooter";
import { VilleProvider } from "@/context/VilleContext";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <VilleProvider>
      <div className="min-h-screen bg-[#020c18] text-[#e0f2fe] font-sans">
        <Navbar />
        <div className="pt-[64px] pb-[140px] sm:pb-0">
          {children}
        </div>
        <PWAFooter />
      </div>
    </VilleProvider>
  );
}
