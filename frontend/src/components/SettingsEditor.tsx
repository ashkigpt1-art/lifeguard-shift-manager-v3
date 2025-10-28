import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { GlowButton } from "./Buttons";
import { api, SettingsPayload } from "../lib/api";
import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

export function SettingsEditor() {
  const [text, setText] = useState("");
  const queryClient = useQueryClient();

  useQuery({
    queryKey: ["settings"],
    queryFn: async () => {
      const res = await api.get("/settings");
      const data = res.data as SettingsPayload;
      setText(stringifyYaml(data));
      return data;
    }
  });

  const mutation = useMutation({
    mutationFn: async (payload: SettingsPayload) => {
      await api.put("/settings", payload);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["settings"] })
  });

  const handleSave = () => {
    try {
      const parsed = parseYaml(text) as SettingsPayload;
      mutation.mutate(parsed);
    } catch (error) {
      alert("فرمت تنظیمات نامعتبر است");
    }
  };

  const handleReset = async () => {
    const response = await api.get("/settings/export", { responseType: "text" });
    if (response.status === 200) {
      setText(response.data as string);
    }
  };

  return (
    <div className="space-y-3">
      <textarea
        className="w-full min-h-[220px] rounded-xl bg-surfaceAlt/60 p-4 text-sm text-muted focus:outline-none focus:ring-2 focus:ring-accent/40"
        value={text}
        onChange={(event) => setText(event.target.value)}
      />
      <div className="flex flex-wrap gap-2">
        <GlowButton icon="💾" onClick={handleSave}>
          ذخیره
        </GlowButton>
        <GlowButton icon="↩️" variant="ghost" onClick={() => queryClient.invalidateQueries({ queryKey: ["settings"] })}>
          بارگذاری
        </GlowButton>
        <GlowButton icon="🔄" variant="ghost" onClick={handleReset}>
          ریست نمونه
        </GlowButton>
      </div>
    </div>
  );
}
