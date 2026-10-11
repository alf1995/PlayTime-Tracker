import { pathToFileURL } from "node:url";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const api = {
  _version: 2,
  callable: () => async () => ({}),
  addEventListener: (_event, callback) => callback,
  removeEventListener: () => {},
  toaster: { toast: () => {} },
  useQuickAccessVisible: () => false,
};

globalThis.window = {
  __DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit: {
    connect: () => api,
  },
};
globalThis.SP_JSX = {
  jsx: (type, props) => ({ type, props }),
  jsxs: (type, props) => ({ type, props }),
  Fragment: Symbol("Fragment"),
};
globalThis.DFL = {
  PanelSection: () => {},
  PanelSectionRow: () => {},
  ButtonItem: () => {},
  ToggleField: () => {},
  staticClasses: { Title: "DeckyTitle" },
};

const dashboard = {
  summary: { today_ms: 120000, week_ms: 120000, month_ms: 120000, year_ms: 120000, total_ms: 120000 },
  series: Array.from({ length: 7 }, (_, i) => ({ day: `2026-10-${String(i + 1).padStart(2, "0")}`, ms: i * 60000 })),
  games: [{ appid: "570", name: "Dota 2", total_ms: 120000, sessions: 1, last_seen_ms: Date.now() }],
  tracker: {
    status: "running", appid: "570", name: "Dota 2", paused: false,
    suspended: false, detection_method: "linux_proc_steam_environment",
    foreground_verified: false, power_signals_available: true, detector_error: null,
  },
  settings: { language: "es", daily_limit_minutes: 120, break_interval_minutes: 60, notifications: true, tracking_enabled: true },
};
const detail = {
  game: dashboard.games[0],
  summary: dashboard.summary,
  series: dashboard.series,
  sessions: [{ id: 1, started_ms: Date.now(), duration_ms: 120000, ended_reason: "closed" }],
  energy: { avg_watts: null, samples: 0 },
};

let values = [];
let position = 0;
globalThis.SP_REACT = {
  useState: (initial) => [values[position++] ?? initial, () => {}],
  useCallback: callback => callback,
  useMemo: callback => callback(),
  useEffect: () => {},
};

const pluginModule = await import(pathToFileURL(resolve(root, "dist/index.js")).href);
const plugin = pluginModule.default();

function find(element, predicate) {
  if (!element || typeof element !== "object") return null;
  if (predicate(element)) return element;
  const children = element.props?.children;
  const list = Array.isArray(children) ? children : [children];
  for (const child of list) {
    const match = find(child, predicate);
    if (match) return match;
  }
  return null;
}

for (const [view, selectedDetail] of [
  ["overview", null], ["games", null], ["games", detail], ["settings", null],
]) {
  values = [dashboard, selectedDetail, view, false, ""];
  position = 0;
  const tree = plugin.content.type({});
  const viewElement = find(tree, element =>
    typeof element.type === "function" && ["Overview", "Games", "Settings"].includes(element.type.name)
  );
  if (!viewElement) throw new Error(`Missing rendered view: ${view}`);
  const viewTree = viewElement.type(viewElement.props);
  if (!viewTree || !viewTree.props?.children) throw new Error(`Invalid view: ${view}`);
}

plugin.onDismount();
console.log("View smoke test passed: overview, games list, game detail, settings.");
