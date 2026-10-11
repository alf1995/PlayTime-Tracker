import React from "react";
import { ButtonItem, PanelSection, PanelSectionRow, ToggleField } from "@decky/ui";
import type { Dashboard, Settings as PluginSettings, SettingLanguage, Translate } from "../types";
import { Glyph } from "../components/Glyph";
import { SectionHeading } from "../components/Ui";

type Props = {
  data: Dashboard;
  t: Translate;
  busy: boolean;
  onSetting: (key: keyof PluginSettings, value: string | number | boolean) => void;
  onRotate: (key: "daily_limit_minutes" | "break_interval_minutes", choices: number[]) => void;
  onExport: (format: "json" | "csv") => void;
  onRefresh: () => void;
};

const LANGUAGE_OPTIONS: SettingLanguage[] = ["auto", "es", "en"];
const DAILY_LIMITS = [0, 30, 60, 90, 120, 180, 240];
const BREAK_INTERVALS = [0, 30, 45, 60, 90, 120];

export function Settings({ data, t, busy, onSetting, onRotate, onExport, onRefresh }: Props) {
  const { settings, tracker } = data;

  return (
    <>
      <SectionHeading label={t("language")} icon="settings"/>
      <div className="ptt-language-options">
        {LANGUAGE_OPTIONS.map(code => (
          <div
            className={`ptt-language-option ${settings.language === code ? "ptt-language-option--active" : ""}`}
            key={code}
          >
            <ButtonItem layout="below" onClick={() => onSetting("language", code)}>
              <span className="ptt-inline">
                {settings.language === code && <Glyph name="check" size={13}/>}
                {t(code === "auto" ? "automatic" : code === "en" ? "english" : "spanish")}
              </span>
            </ButtonItem>
          </div>
        ))}
      </div>

      <SectionHeading label={t("tracking")} icon="gamepad"/>
      <PanelSection>
        <PanelSectionRow>
          <ToggleField
            label={t("monitoring")}
            checked={settings.tracking_enabled}
            onChange={(value: boolean) => onSetting("tracking_enabled", value)}
          />
        </PanelSectionRow>
        <PanelSectionRow>
          <ToggleField
            label={t("notifications")}
            checked={settings.notifications}
            onChange={(value: boolean) => onSetting("notifications", value)}
          />
        </PanelSectionRow>
      </PanelSection>

      <div className="ptt-setting-item">
        <div><strong>{t("dailyLimit")}</strong><small>{t("tapToChange")}</small></div>
        <ButtonItem layout="below" onClick={() => onRotate("daily_limit_minutes", DAILY_LIMITS)}>
          {settings.daily_limit_minutes ? `${settings.daily_limit_minutes} ${t("minutes")}` : t("disabledLabel")} ▸
        </ButtonItem>
      </div>
      <div className="ptt-setting-item">
        <div><strong>{t("breakEvery")}</strong><small>{t("tapToChange")}</small></div>
        <ButtonItem layout="below" onClick={() => onRotate("break_interval_minutes", BREAK_INTERVALS)}>
          {settings.break_interval_minutes ? `${settings.break_interval_minutes} ${t("minutes")}` : t("disabledLabel")} ▸
        </ButtonItem>
      </div>

      <SectionHeading label={t("exports")} icon="database"/>
      <div className="ptt-export-actions">
        <ButtonItem layout="below" disabled={busy} onClick={() => onExport("json")}>{t("exportJson")}</ButtonItem>
        <ButtonItem layout="below" disabled={busy} onClick={() => onExport("csv")}>{t("exportCsv")}</ButtonItem>
      </div>

      <SectionHeading label={t("unknownPlatform")} icon="settings"/>
      <div className="ptt-diagnostics">
        <div><span>{t("detector")}</span><strong>{tracker.detection_method}</strong></div>
        <div>
          <span>{t("powerSignals")}</span>
          <strong>{tracker.power_signals_available ? t("available") : t("unavailable")}</strong>
        </div>
        {tracker.detector_error && (
          <div><span>{t("error")}</span><strong>{tracker.detector_error}</strong></div>
        )}
        <p>{t("note")}</p>
      </div>
      <div className="ptt-quick-action">
        <ButtonItem layout="below" onClick={onRefresh}>
          <span className="ptt-inline"><Glyph name="refresh" size={15}/>{t("restart")}</span>
        </ButtonItem>
      </div>
    </>
  );
}
