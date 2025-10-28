import { useEffect, useState } from "react";
import { LongView } from "../components/LongView";
import { GlowButton } from "../components/Buttons";
import { api } from "../lib/api";

export function LongTable() {
  const [data, setData] = useState<Record<string, string>[]>([]);

  const fetchHistory = async () => {
    const res = await api.get<Record<string, string>[]>("/allocate/history");
    setData(res.data);
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <GlowButton icon="↻" variant="ghost" onClick={fetchHistory}>
          تازه‌سازی
        </GlowButton>
        <GlowButton icon="⬇️" variant="ghost" onClick={() => window.open(`${api.defaults.baseURL}/allocate/export/long.csv`)}>
          دانلود CSV
        </GlowButton>
      </div>
      <LongView data={data} />
    </div>
  );
}
