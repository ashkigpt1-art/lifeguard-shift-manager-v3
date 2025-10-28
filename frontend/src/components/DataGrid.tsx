import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, Lifeguard, Location } from "../lib/api";
import { GlowButton } from "./Buttons";
import { motion } from "framer-motion";
import { useRef, useState, type ChangeEvent } from "react";

interface DataGridProps {
  type: "guards" | "locations";
}

const headers = {
  guards: ["نام", "تجربه", "حضور", "مسئولیت", "تیم"],
  locations: ["لوکیشن", "سختی", "آبی", "فعال"]
};

export function DataGrid({ type }: DataGridProps) {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { data } = useQuery({
    queryKey: [type],
    queryFn: async () => {
      const path = type === "guards" ? "/lifeguards" : "/locations";
      const res = await api.get(path);
      return res.data as (Lifeguard | Location)[];
    }
  });

  const [form, setForm] = useState(
    type === "guards"
      ? { name: "", experience: "medium", role: "ناجی", present: true }
      : { name: "", difficulty: "medium", is_water: false, active_today: true }
  );

  const removeMutation = useMutation({
    mutationFn: async (id: number) => {
      const path = type === "guards" ? "/lifeguards" : "/locations";
      await api.delete(`${path}/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [type] })
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const path = type === "guards" ? "/lifeguards" : "/locations";
      await api.post(path, form);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [type] });
      setForm(
        type === "guards"
          ? { name: "", experience: "medium", role: "ناجی", present: true }
          : { name: "", difficulty: "medium", is_water: false, active_today: true }
      );
    }
  });

  const importMutation = useMutation({
    mutationFn: async (file: File) => {
      const path = type === "guards" ? "/lifeguards/import" : "/locations/import";
      const formData = new FormData();
      formData.append("file", file);
      await api.post(path, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [type] })
  });

  const handleImport = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      importMutation.mutate(file);
      event.target.value = "";
    }
  };

  const handleExport = () => {
    const path = type === "guards" ? "/lifeguards" : "/locations";
    window.open(`${api.defaults.baseURL}${path}/export`, "_blank");
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-3 rounded-xl bg-surfaceAlt/40 p-4 text-sm">
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileChange}
        />
        <div className="flex flex-col">
          <label className="text-muted">نام</label>
          <input
            value={(form as any).name ?? ""}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="rounded-lg bg-surface/60 px-3 py-2 text-text focus:outline-none focus:ring-2 focus:ring-accent/40"
          />
        </div>
        {type === "guards" ? (
          <>
            <div className="flex flex-col">
              <label className="text-muted">تجربه</label>
              <select
                value={(form as any).experience}
                onChange={(e) => setForm({ ...form, experience: e.target.value })}
                className="rounded-lg bg-surface/60 px-3 py-2 text-text focus:outline-none focus:ring-2 focus:ring-accent/40"
              >
                <option value="expert">expert</option>
                <option value="medium">medium</option>
                <option value="low">low</option>
              </select>
            </div>
            <div className="flex flex-col">
              <label className="text-muted">مسئولیت</label>
              <select
                value={(form as any).role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
                className="rounded-lg bg-surface/60 px-3 py-2 text-text focus:outline-none focus:ring-2 focus:ring-accent/40"
              >
                <option value="ناجی">ناجی</option>
                <option value="ناجی چک">ناجی چک</option>
                <option value="سر ناجی">سر ناجی</option>
              </select>
            </div>
            <label className="flex items-center gap-2 text-muted">
              <input
                type="checkbox"
                checked={(form as any).present}
                onChange={(e) => setForm({ ...form, present: e.target.checked })}
              />
              حضور
            </label>
          </>
        ) : (
          <>
            <div className="flex flex-col">
              <label className="text-muted">سختی</label>
              <select
                value={(form as any).difficulty}
                onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
                className="rounded-lg bg-surface/60 px-3 py-2 text-text focus:outline-none focus:ring-2 focus:ring-accent/40"
              >
                <option value="easy">easy</option>
                <option value="medium">medium</option>
                <option value="hard">hard</option>
              </select>
            </div>
            <label className="flex items-center gap-2 text-muted">
              <input
                type="checkbox"
                checked={(form as any).is_water}
                onChange={(e) => setForm({ ...form, is_water: e.target.checked })}
              />
              آبی
            </label>
            <label className="flex items-center gap-2 text-muted">
              <input
                type="checkbox"
                checked={(form as any).active_today}
                onChange={(e) => setForm({ ...form, active_today: e.target.checked })}
              />
              فعال
            </label>
          </>
        )}
        <GlowButton icon="➕" type="button" onClick={() => createMutation.mutate()}>
          افزودن
        </GlowButton>
        <GlowButton icon="⬆️" type="button" variant="ghost" onClick={handleImport}>
          ورود CSV
        </GlowButton>
        <GlowButton icon="⬇️" type="button" variant="ghost" onClick={handleExport}>
          خروجی CSV
        </GlowButton>
      </div>
      <div className="overflow-x-auto rounded-xl border border-surfaceAlt/40">
        <table className="min-w-full divide-y divide-surfaceAlt">
          <thead className="bg-surface/70">
            <tr>
              {headers[type].map((header) => (
                <th key={header} className="px-4 py-3 text-right text-sm text-muted">
                  {header}
                </th>
              ))}
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-surfaceAlt/40">
            {data?.map((item: any) => (
              <motion.tr key={item.id} initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} className="hover:bg-surfaceAlt/30">
                {type === "guards" ? (
                  <>
                    <td className="px-4 py-3">{item.name}</td>
                    <td className="px-4 py-3 text-sm text-muted">{item.experience}</td>
                    <td className="px-4 py-3 text-sm text-muted">{item.present ? "✅" : "❌"}</td>
                    <td className="px-4 py-3 text-sm text-muted">{item.role}</td>
                    <td className="px-4 py-3 text-sm text-muted">{item.team ?? "-"}</td>
                  </>
                ) : (
                  <>
                    <td className="px-4 py-3">{item.name}</td>
                    <td className="px-4 py-3 text-sm text-muted">{item.difficulty}</td>
                    <td className="px-4 py-3 text-sm text-muted">{item.is_water ? "💧" : "🏝"}</td>
                    <td className="px-4 py-3 text-sm text-muted">{item.active_today ? "✅" : "❌"}</td>
                  </>
                )}
                <td className="px-4 py-3 text-left">
                  <GlowButton
                    icon="🗑"
                    variant="ghost"
                    onClick={() => removeMutation.mutate(item.id)}
                    className="text-xs"
                  >
                    حذف
                  </GlowButton>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
