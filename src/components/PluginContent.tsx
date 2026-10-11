import React, { useCallback, useEffect, useState } from "react";
import { useQuickAccessVisible, toaster } from "@decky/api";
import { ButtonItem } from "@decky/ui";
import { languageFrom, translate } from "../i18n/translations";
import { getDashboard, getGameDetail, updateSetting, setPaused, exportData, withTimeout } from "../api/decky";
import type { Dashboard, Detail, Settings, View } from "../types";
import { NavTabs } from "./NavTabs";
import { Overview } from "../views/Overview";
import { Games } from "../views/Games";
import { Settings as SettingsView } from "../views/Settings";
import { pttCSS } from "../styles";

export function PluginContent() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [view, setView] = useState<View>("overview");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const visible = useQuickAccessVisible();
  const settings = data?.settings;
  const lang = languageFrom(settings?.language || "auto");
  const t = useCallback((key: Parameters<typeof translate>[1]) => translate(lang, key), [lang]);

  const refresh = useCallback(async () => {
    try {
      const dashboard = await withTimeout(getDashboard());
      setData(dashboard);
      setError("");
    } catch (err) {
      setError(String(err).includes("BACKEND_TIMEOUT") ? "BACKEND_TIMEOUT" : String(err));
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => {
    if (!visible) return;
    void refresh();
    const timer = setInterval(() => { void refresh(); }, 10000);
    return () => clearInterval(timer);
  }, [visible, refresh]);

  async function setting(key: keyof Settings, value: string | number | boolean) {
    try {
      const updated = await withTimeout(updateSetting(key, value));
      setData(current => current ? { ...current, settings: updated } : current);
      setError("");
    } catch (err) {
      setError(String(err));
    }
  }

  async function selectGame(appid: string) {
    setBusy(true);
    try {
      setDetail(await withTimeout(getGameDetail(appid)));
      setError("");
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  async function backup(fmt: "json" | "csv") {
    setBusy(true);
    try {
      const result = await withTimeout(exportData(fmt), 20000);
      toaster.toast({ title: t("exportSuccess"), body: result.path });
    } catch (err) {
      toaster.toast({ title: t("exportFailed"), body: String(err) });
    } finally {
      setBusy(false);
    }
  }

  async function pauseTracking() {
    if (!data) return;
    setBusy(true);
    try {
      await withTimeout(setPaused(!data.tracker.paused));
      await refresh();
    } catch (err) {
      setError(String(err));
    } finally {
      setBusy(false);
    }
  }

  function rotate(key: "daily_limit_minutes" | "break_interval_minutes", choices: number[]) {
    if (!settings) return;
    const idx = choices.indexOf(settings[key]);
    void setting(key, choices[(idx + 1) % choices.length]);
  }

  function navigate(next: View) {
    setView(next);
    setDetail(null);
  }

  return <div className="ptt-root"><style>{pttCSS}</style>
    <div className="ptt-topline"><span className="ptt-kicker">{t("subtitle")}</span><span className="ptt-version">v0.1.5</span></div>
    <NavTabs view={view} onChange={navigate} t={t}/>
    {error && <div className="ptt-error" role="alert"><strong>{t("error")}</strong><p>{error === "BACKEND_TIMEOUT" ? t("backendTimeout") : error}</p><ButtonItem layout="below" onClick={() => void refresh()}>{t("retry")}</ButtonItem></div>}
    {!data && !error && <div className="ptt-loading"><span className="ptt-spinner"/>{t("loading")}</div>}
    {data && view === "overview" && <Overview data={data} lang={lang} t={t} busy={busy} onPause={() => void pauseTracking()} onNavigate={navigate}/>}
    {data && view === "games" && <Games data={data} detail={detail} lang={lang} t={t} busy={busy} onSelectGame={(appid) => void selectGame(appid)} onBack={() => setDetail(null)}/>}
    {data && view === "settings" && <SettingsView data={data} t={t} busy={busy} onSetting={(key, value) => void setting(key, value)} onRotate={rotate} onExport={(fmt) => void backup(fmt)} onRefresh={() => void refresh()}/>}
  </div>;
}
