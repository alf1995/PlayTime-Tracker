import { callable } from "@decky/api";
import type { Dashboard, Detail, Settings, Tracker } from "../types";

export const getDashboard = callable<[], Dashboard>("get_dashboard");
export const getGameDetail = callable<[appid: string], Detail | null>("get_game_detail");
export const updateSetting = callable<[key: string, value: string | number | boolean], Settings>("update_setting");
export const setPaused = callable<[paused: boolean], Tracker>("set_paused");
export const exportData = callable<[format: string], { path: string }>("export_data");

export async function withTimeout<T>(operation: Promise<T>, durationMs = 8000): Promise<T> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    return await Promise.race([
      operation,
      new Promise<T>((_resolve, reject) => {
        timer = setTimeout(() => reject(new Error("BACKEND_TIMEOUT")), durationMs);
      }),
    ]);
  } finally {
    if (timer !== undefined) clearTimeout(timer);
  }
}
