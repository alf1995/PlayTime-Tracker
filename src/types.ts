import type { Key, Language, SettingLanguage } from "./i18n/translations";

export type Tracker = {
  status: string;
  appid: string | null;
  name: string | null;
  paused: boolean;
  suspended: boolean;
  detection_method: string;
  foreground_verified: boolean;
  power_signals_available: boolean;
  detector_error: string | null;
};

export type Game = {
  appid: string;
  name: string;
  total_ms: number;
  sessions: number;
  last_seen_ms: number;
};

export type Summary = {
  today_ms: number;
  week_ms: number;
  month_ms: number;
  year_ms: number;
  total_ms: number;
};

export type Day = { day: string; ms: number };

export type Settings = {
  language: SettingLanguage;
  daily_limit_minutes: number;
  break_interval_minutes: number;
  notifications: boolean;
  tracking_enabled: boolean;
};

export type Dashboard = {
  summary: Summary;
  series: Day[];
  games: Game[];
  settings: Settings;
  tracker: Tracker;
};

export type Detail = {
  game: Game;
  summary: Summary;
  series: Day[];
  sessions: { id: number; started_ms: number; duration_ms: number; ended_reason: string }[];
  energy: { avg_watts: number | null; samples: number };
};

export type View = "overview" | "games" | "settings";
export type GlyphName = "clock" | "gamepad" | "chart" | "settings" | "pause" | "play" | "bolt" | "database" | "arrow" | "refresh" | "check";
export type Translate = (key: Key) => string;
export type { Language, SettingLanguage };
