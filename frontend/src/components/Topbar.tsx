import { GlowButton } from "./Buttons";
import { useUIStore } from "../store/useUI";

export function Topbar() {
  const { activeTab, setTab } = useUIStore();
  return (
    <header className="sticky top-0 z-10 border-b border-surfaceAlt/50 bg-bg/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <h1 className="text-lg font-bold text-accent">مدیریت شیفت ناجیان</h1>
        <nav className="flex gap-2">
          <GlowButton icon="🗂" variant={activeTab === "data" ? "primary" : "ghost"} onClick={() => setTab("data")}>
            داده‌ها و تنظیمات
          </GlowButton>
          <GlowButton icon="🚀" variant={activeTab === "allocate" ? "primary" : "ghost"} onClick={() => setTab("allocate")}>
            محاسبه شیفت‌ها
          </GlowButton>
          <GlowButton icon="🧾" variant={activeTab === "long" ? "primary" : "ghost"} onClick={() => setTab("long")}>
            نمای تفصیلی
          </GlowButton>
        </nav>
      </div>
    </header>
  );
}
