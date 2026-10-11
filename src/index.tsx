import React from "react";
import { addEventListener, definePlugin, removeEventListener, toaster } from "@decky/api";
import { staticClasses } from "@decky/ui";
import { getDashboard, withTimeout } from "./api/decky";
import { PluginContent } from "./components/PluginContent";
import { languageFrom, translate, type SettingLanguage } from "./i18n/translations";

export default definePlugin(() => {
  const notice = addEventListener<[payload: { type: string; minutes: number }]>(
    "playtime_notice",
    payload => {
      void withTimeout(getDashboard())
        .then(dashboard => dashboard.settings.language)
        .catch(() => "auto" as SettingLanguage)
        .then(selected => {
          const lang = languageFrom(selected);
          const isBreak = payload.type === "break";
          toaster.toast({
            title: translate(lang, isBreak ? "breakReminder" : "limitReached"),
            body: translate(lang, isBreak ? "breakBody" : "limitBody", { minutes: payload.minutes }),
          });
        });
    }
  );

  return {
    name: "PlayTime Tracker",
    titleView: <div className={staticClasses.Title}>PlayTime Tracker</div>,
    content: <PluginContent />,
    icon: <span style={{ fontSize: 21 }}>◷</span>,
    onDismount() { removeEventListener("playtime_notice", notice); },
  };
});
