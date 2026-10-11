import React from "react";
import type { Key } from "../i18n/translations";
import type { GlyphName, Translate } from "../types";
import { Glyph } from "./Glyph";

const STATUS_KEYS: Record<string, Key> = {
  running: "running",
  paused: "paused",
  suspended: "suspended",
  idle: "idle",
  unknown: "unknown",
  ambiguous: "ambiguous",
  disabled: "disabled",
};

export function StatusPill({ status, t }: { status: string; t: Translate }) {
  const tone = status === "running"
    ? "active"
    : status === "paused" || status === "suspended" ? "warn" : "idle";

  return (
    <span className={`ptt-status ptt-status--${tone}`}>
      <span className="ptt-status-dot"/>
      {t(STATUS_KEYS[status] || "unknown")}
    </span>
  );
}

export function SectionHeading({ label, aside, icon }: {
  label: string;
  aside?: string;
  icon: GlyphName;
}) {
  return (
    <div className="ptt-section-heading">
      <span className="ptt-section-icon"><Glyph name={icon} size={16}/></span>
      <span className="ptt-section-label">{label}</span>
      {aside && <span className="ptt-section-aside">{aside}</span>}
    </div>
  );
}

export function Stat({ label, value, kind }: {
  label: string;
  value: string;
  kind?: "primary";
}) {
  return (
    <div className={`ptt-stat ${kind ? "ptt-stat--primary" : ""}`}>
      <span className="ptt-stat-label">{label}</span>
      <strong className="ptt-stat-value">{value}</strong>
    </div>
  );
}
