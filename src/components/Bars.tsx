import React, { useMemo } from "react";
import { translate } from "../i18n/translations";
import type { Day, Language } from "../types";
import { duration } from "../utils/format";

export function Bars({ data, lang }: { data: Day[]; lang: Language }) {
  const formatter = useMemo(() => new Intl.DateTimeFormat(lang,{weekday:"short",timeZone:"UTC"}),[lang]);
  const values = data.slice(-7);
  const max = Math.max(1,...values.map(x=>x.ms));
  const empty = values.every(x => x.ms <= 0);
  return <div className="ptt-chart" role="img" aria-label={translate(lang,"activity")}>
    <svg viewBox="0 0 320 133" preserveAspectRatio="xMidYMid meet" width="100%" height="133">
      {[25,58,91].map(y => <line key={y} x1="8" y1={y} x2="312" y2={y} stroke="rgba(184,208,230,.12)" strokeDasharray="3 5" />)}
      {values.map((point,i)=>{
        const height = point.ms > 0 ? Math.max(4,Math.round(point.ms/max*79)) : 3;
        const x = 15 + i * (290/Math.max(values.length,1));
        const weekday = formatter.format(new Date(`${point.day}T12:00:00Z`)).replace(".", "");
        return <g key={point.day}>
          <rect x={x} y={96-height} width="27" height={height} rx="5" fill={point.ms ? "#65bff6" : "rgba(132,162,189,.24)"} />
          <text x={x+13.5} y="119" textAnchor="middle" fill="#afc2d1" fontSize="11">{weekday}</text>
          <title>{`${point.day}: ${duration(point.ms,lang)}`}</title>
        </g>;
      })}
    </svg>
    {empty && <div className="ptt-chart-empty">{translate(lang,"noActivity")}</div>}
  </div>;
}
