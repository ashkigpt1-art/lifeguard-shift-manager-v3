import { useMutation } from "@tanstack/react-query";
import { GlowButton } from "../components/Buttons";
import { WideView } from "../components/WideView";
import { api, AllocationResult } from "../lib/api";
import { motion } from "framer-motion";
import { useState } from "react";

export function Allocate() {
  const [data, setData] = useState<AllocationResult | null>(null);
  const mutation = useMutation({
    mutationFn: async () => {
      const res = await api.post<AllocationResult>("/allocate");
      return res.data;
    },
    onSuccess: (payload) => setData(payload)
  });

  const handleDownload = (kind: "wide" | "long") => {
    window.open(`${api.defaults.baseURL}/allocate/export/${kind}.csv`, "_blank");
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} className="flex flex-wrap items-center gap-3">
        <GlowButton icon="🚀" onClick={() => mutation.mutate()}>
          محاسبه شیفت‌ها
        </GlowButton>
        {data ? (
          <>
            <GlowButton icon="⬇️" variant="ghost" onClick={() => handleDownload("wide")}>
              دانلود Wide
            </GlowButton>
            <GlowButton icon="⬇️" variant="ghost" onClick={() => handleDownload("long")}>
              دانلود Long
            </GlowButton>
          </>
        ) : null}
      </motion.div>
      {data ? (
        <div className="space-y-6">
          <p className="text-muted">{data.caption}</p>
          <WideView data={data.wide} />
          <section className="space-y-3">
            <h3 className="text-sm font-semibold text-text">تیم حاضر</h3>
            <div className="grid gap-2 sm:grid-cols-2 md:grid-cols-3">
              {data.team.map((member) => (
                <div key={member.id as number} className="rounded-xl bg-surfaceAlt/50 p-3 text-sm text-muted">
                  <p className="text-text">{member.name}</p>
                  <p>{member.role}</p>
                  <p>{member.experience}</p>
                </div>
              ))}
            </div>
          </section>
          <section className="space-y-3">
            <h3 className="text-sm font-semibold text-text">تاریخچه روز</h3>
            <div className="grid gap-2 md:grid-cols-2">
              {data.history.map((entry, index) => (
                <div key={`${entry.guard_name}-${index}`} className="rounded-xl bg-surfaceAlt/40 p-3 text-xs text-muted">
                  <p className="text-text">{entry.guard_name}</p>
                  <p>{entry.location_name}</p>
                  <p>
                    {entry.start} - {entry.end}
                  </p>
                  <p>{entry.kind}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      ) : (
        <p className="text-muted">برای مشاهده جدول، روی محاسبه شیفت‌ها کلیک کنید.</p>
      )}
    </div>
  );
}
