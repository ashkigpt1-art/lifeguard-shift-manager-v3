import { create } from "zustand";

interface UIState {
  activeTab: "data" | "allocate" | "long";
  setTab: (tab: UIState["activeTab"]) => void;
}

export const useUIStore = create<UIState>((set) => ({
  activeTab: "data",
  setTab: (tab) => set({ activeTab: tab })
}));
