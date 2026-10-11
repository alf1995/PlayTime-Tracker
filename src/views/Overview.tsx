import React from "react";
import { ButtonItem } from "@decky/ui";
import type { Dashboard, Language, Translate, View } from "../types";
import { Glyph } from "../components/Glyph";
import { Bars } from "../components/Bars";
import { SectionHeading, Stat, StatusPill } from "../components/Ui";
import { duration } from "../utils/format";

type Props = {
  data: Dashboard;
  lang: Language;
  t: Translate;
  busy: boolean;
  onPause: () => void;
  onNavigate: (view: View) => void;
};

export function Overview({ data, lang, t, busy, onPause, onNavigate }: Props) {
  const { tracker, summary, series, games, settings } = data;

  return (
    <>
      <div className="ptt-hero">
        <div className="ptt-hero-header">
          <span className="ptt-hero-caption">
            <Glyph name="gamepad" size={16}/>{t("active")}
          </span>
          <StatusPill status={tracker.status} t={t}/>
        </div>
        <div className="ptt-hero-body">
          <span className="ptt-game-avatar"><Glyph name="gamepad" size={23}/></span>
          <div className="ptt-hero-info">
            <strong>{tracker.name || t("noGame")}</strong>
            <small>{tracker.status === "running" ? t("gameDetectedHint") : t("waitingForGame")}</small>
          </div>
        </div>
        <div className="ptt-hero-footer">
          <span>{t("notVerified")}</span>
          <ButtonItem layout="below" disabled={busy || !settings.tracking_enabled} onClick={onPause}>
            <span className="ptt-inline">
              <Glyph name={tracker.paused ? "play" : "pause"} size={14}/>
              {t(tracker.paused ? "resume" : "pause")}
            </span>
          </ButtonItem>
        </div>
      </div>

      <SectionHeading label={t("playtime")} icon="clock" aside={t("localData")}/>
      <div className="ptt-stats-grid">
        <Stat kind="primary" label={t("today")} value={duration(summary.today_ms, lang)}/>
        <Stat kind="primary" label={t("week")} value={duration(summary.week_ms, lang)}/>
      </div>
      <div className="ptt-stats-grid ptt-stats-grid--three">
        <Stat label={t("month")} value={duration(summary.month_ms, lang)}/>
        <Stat label={t("year")} value={duration(summary.year_ms, lang)}/>
        <Stat label={t("total")} value={duration(summary.total_ms, lang)}/>
      </div>

      <SectionHeading label={t("activity")} icon="chart" aside={t("dailyActivity")}/>
      <Bars data={series} lang={lang}/>
      <div className="ptt-footer-note">{t("readOnly")}</div>
      <div className="ptt-quick-action">
        <ButtonItem layout="below" onClick={() => onNavigate("games")}>
          <span className="ptt-inline">
            {t("seeGames")}&nbsp; ({games.length}) <Glyph name="arrow" size={16}/>
          </span>
        </ButtonItem>
      </div>
    </>
  );
}
