import React from "react";
import type { GlyphName } from "../types";

export function Glyph({ name, size = 18 }: { name: GlyphName; size?: number }) {
  const props = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.9, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true as const };
  switch (name) {
    case "clock": return <svg {...props}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>;
    case "gamepad": return <svg {...props}><path d="M6.6 8.2h10.8a3.4 3.4 0 0 1 3.3 2.7l1 5a2.3 2.3 0 0 1-3.6 2.3l-2.2-1.6H8.1l-2.2 1.6a2.3 2.3 0 0 1-3.6-2.3l1-5a3.4 3.4 0 0 1 3.3-2.7Z"/><path d="M7 12.7h5M9.5 10.2v5M16 12h.01M18.5 14h.01"/></svg>;
    case "chart": return <svg {...props}><path d="M4 20V10M10 20V5M16 20v-8M22 20V8"/></svg>;
    case "settings": return <svg {...props}><circle cx="12" cy="12" r="3"/><path d="m19 13 2-1-2-1-.5-2 1-2-2-2-2 1-2-.5-1-2-1 2-2 .5-2-1-2 2 1 2-.5 2-2 1 2 1 .5 2-1 2 2 2 2-1 2 .5 1 2 1-2 2-.5 2 1 2-2-1-2Z"/></svg>;
    case "pause": return <svg {...props}><path d="M8 5v14M16 5v14"/></svg>;
    case "play": return <svg {...props}><path d="m8 5 11 7-11 7z"/></svg>;
    case "bolt": return <svg {...props}><path d="m13 2-9 12h7l-1 8 10-12h-7z"/></svg>;
    case "database": return <svg {...props}><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/></svg>;
    case "arrow": return <svg {...props}><path d="m9 18 6-6-6-6"/></svg>;
    case "refresh": return <svg {...props}><path d="M20 11a8 8 0 1 0-2.5 6M20 4v7h-7"/></svg>;
    case "check": return <svg {...props}><path d="m5 12 4 4 10-9"/></svg>;
  }
}
