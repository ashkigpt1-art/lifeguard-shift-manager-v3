import { DataGrid } from "../components/DataGrid";
import { SettingsEditor } from "../components/SettingsEditor";

export function DataAndSettings() {
  return (
    <div className="space-y-8">
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-text">لیست ناجیان</h2>
        <DataGrid type="guards" />
      </section>
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-text">لوکیشن‌ها</h2>
        <DataGrid type="locations" />
      </section>
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-text">تنظیمات</h2>
        <SettingsEditor />
      </section>
    </div>
  );
}
