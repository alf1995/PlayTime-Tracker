import { translate } from "../i18n/translations";
import type { Language } from "../types";

export function duration(ms: number, lang: Language): string {
  const minutes = Math.floor(Math.max(0, Number.isFinite(ms) ? ms : 0) / 60000);
  return `${Math.floor(minutes / 60)}${translate(lang,"hoursShort")} ${String(minutes % 60).padStart(2,"0")}${translate(lang,"minShort")}`;
}
export function niceDate(ms: number, lang: Language): string {
  return new Intl.DateTimeFormat(lang, { day: "numeric", month: "short" }).format(new Date(ms));
}
