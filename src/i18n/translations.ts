import { english } from "./en";
import { spanish } from "./es";

export type Language = "en" | "es";
export type SettingLanguage = Language | "auto";
export type Key = keyof typeof english;

export const translations: Record<Language, Record<Key, string>> = {
  en: english,
  es: spanish,
};

export function languageFrom(setting: SettingLanguage): Language {
  if (setting === "en" || setting === "es") return setting;
  return typeof navigator !== "undefined" && navigator.language.toLowerCase().startsWith("es")
    ? "es"
    : "en";
}

export function translate(
  language: Language,
  key: Key,
  values: Record<string, string | number> = {},
): string {
  return translations[language][key].replace(
    /\{(\w+)\}/g,
    (_match, name: string) => String(values[name] ?? ""),
  );
}
