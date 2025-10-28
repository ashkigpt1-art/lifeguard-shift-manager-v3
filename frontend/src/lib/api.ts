import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1"
});

export interface Lifeguard {
  id: number;
  name: string;
  experience: "expert" | "medium" | "low";
  role: "ناجی" | "ناجی چک" | "سر ناجی";
  present: boolean;
  team?: string | null;
  lunch_at: string;
  backup_name: string;
  swap_at: string;
}

export interface Location {
  id: number;
  name: string;
  difficulty: "easy" | "medium" | "hard";
  is_water: boolean;
  active_today: boolean;
}

export interface SettingsPayload {
  start: string;
  end: string;
  shift_hours: number;
  special_hours: number;
  lunch_min: number;
  dinner_min: number;
  shower_min: number;
  max_concurrent_lunch: number;
  check_windows_min: number[];
  check_window_len_min: number;
}

export interface AllocationResult {
  wide: Record<string, string>[];
  long: Record<string, string>[];
  team: Record<string, string | number | null>[];
  history: Record<string, string>[];
  caption: string;
}
