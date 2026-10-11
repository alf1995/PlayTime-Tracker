import React from "react";
import { ButtonItem } from "@decky/ui";
import type { GlyphName, Translate, View } from "../types";
import { Glyph } from "./Glyph";

type Props = {
  view: View;
  onChange: (next: View) => void;
  t: Translate;
};

const TABS: { id: View; glyph: GlyphName }[] = [
  { id: "overview", glyph: "chart" },
  { id: "games", glyph: "gamepad" },
  { id: "settings", glyph: "settings" },
];

export function NavTabs({ view, onChange, t }: Props) {
  return (
    <div className="ptt-tabs">
      {TABS.map(tab => (
        <div key={tab.id} className={`ptt-tab ${tab.id === view ? "ptt-tab--active" : ""}`}>
          <ButtonItem layout="below" onClick={() => onChange(tab.id)}>
            <span className="ptt-tab-content">
              <Glyph name={tab.glyph} size={15}/>
              <span>{t(tab.id)}</span>
            </span>
          </ButtonItem>
        </div>
      ))}
    </div>
  );
}
