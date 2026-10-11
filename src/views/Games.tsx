import React from "react";
import { ButtonItem } from "@decky/ui";
import type { Dashboard, Detail, Language, Translate } from "../types";
import { Glyph } from "../components/Glyph";
import { Bars } from "../components/Bars";
import { SectionHeading, Stat } from "../components/Ui";
import { duration, niceDate } from "../utils/format";

type Props = {
  data: Dashboard;
  detail: Detail | null;
  lang: Language;
  t: Translate;
  busy: boolean;
  onSelectGame: (appid: string) => void;
  onBack: () => void;
};

export function Games({ data, detail, lang, t, busy, onSelectGame, onBack }: Props) {
  if (detail) {
    return (
      <>
        <div className="ptt-detail-back">
          <ButtonItem layout="below" onClick={onBack}>← {t("back")}</ButtonItem>
        </div>
        <div className="ptt-game-header">
          <span className="ptt-game-avatar"><Glyph name="gamepad" size={23}/></span>
          <div>
            <strong>{detail.game.name}</strong>
            <small>AppID: {detail.game.appid} · {detail.game.sessions} {t("sessions").toLowerCase()}</small>
          </div>
        </div>
        <div className="ptt-stats-grid">
          <Stat kind="primary" label={t("today")} value={duration(detail.summary.today_ms, lang)}/>
          <Stat kind="primary" label={t("week")} value={duration(detail.summary.week_ms, lang)}/>
        </div>
        <div className="ptt-stats-grid ptt-stats-grid--single">
          <Stat label={t("total")} value={duration(detail.summary.total_ms, lang)}/>
        </div>
        <SectionHeading label={t("activity")} icon="chart"/>
        <Bars data={detail.series} lang={lang}/>
        <SectionHeading label={t("energy")} icon="bolt"/>
        <div className="ptt-info-card">
          <strong>{detail.energy.avg_watts === null ? t("unavailable") : `${detail.energy.avg_watts} W`}</strong>
          <small>{t("energyNotice")}</small>
        </div>
        <SectionHeading label={t("lastSessions")} icon="clock"/>
        {detail.sessions.length ? detail.sessions.map(session => (
          <div className="ptt-session-row" key={session.id}>
            <span>
              {niceDate(session.started_ms, lang)}
              <small>{new Date(session.started_ms).toLocaleTimeString(lang, { hour: "2-digit", minute: "2-digit" })}</small>
            </span>
            <strong>{duration(session.duration_ms, lang)}</strong>
          </div>
        )) : <div className="ptt-empty">{t("noSessions")}</div>}
      </>
    );
  }

  return (
    <>
      <div className="ptt-list-title">
        <SectionHeading label={t("games")} icon="gamepad" aside={`${data.games.length}`}/>
      </div>
      {data.games.length ? data.games.map((game, index) => (
        <div className="ptt-game-entry" key={game.appid}>
          <ButtonItem layout="below" disabled={busy} onClick={() => onSelectGame(game.appid)}>
            <span className="ptt-game-entry-inner">
              <span className="ptt-game-rank">{String(index + 1).padStart(2, "0")}</span>
              <span className="ptt-game-entry-text">
                <strong>{game.name}</strong>
                <small>
                  {game.sessions} {t("sessions").toLowerCase()} · {game.last_seen_ms ? niceDate(game.last_seen_ms, lang) : "—"}
                </small>
              </span>
              <span className="ptt-game-time">{duration(game.total_ms, lang)}</span>
              <Glyph name="arrow" size={15}/>
            </span>
          </ButtonItem>
        </div>
      )) : (
        <div className="ptt-empty">
          <Glyph name="gamepad" size={28}/>
          <strong>{t("emptyGamesTitle")}</strong>
          <span>{t("noData")}</span>
        </div>
      )}
    </>
  );
}
