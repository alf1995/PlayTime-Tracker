/** Minimal mocked Decky runtime smoke test, no device assertions. */
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
const root = resolve(import.meta.dirname,"..");
const calls = [];
const api = {
  _version: 2,
  callable(name) {return async (...args) => {calls.push({name,args});return {};};},
  addEventListener:(_name,fn)=>fn,
  removeEventListener:()=>{},
  toaster:{toast:()=>{}},
  useQuickAccessVisible:()=>false,
};
globalThis.window={__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit:{connect:()=>api}};
globalThis.SP_JSX={jsx:(type,props)=>({type,props}),jsxs:(type,props)=>({type,props}),Fragment:Symbol("Fragment")};
globalThis.SP_REACT={useState:(initial)=>[initial,()=>{}],useCallback:(fn)=>fn,useMemo:(fn)=>fn(),useEffect:()=>{}};
globalThis.DFL={PanelSection:()=>{},PanelSectionRow:()=>{},ButtonItem:()=>{},ToggleField:()=>{},staticClasses:{Title:"DeckyTitle"}};
const module = await import(pathToFileURL(resolve(root,"dist/index.js")).href);
const plugin = module.default();
if(plugin.name!=="PlayTime Tracker") throw Error("Bad plugin identity");
if(!plugin.content || typeof plugin.content.type!=="function") throw Error("Missing panel");
const content = plugin.content.type({});
if(content?.type!=="div" || !content.props?.children) throw Error("Bad component output");
const styles = content.props.children.find(c=>c?.type === "style");
if(!styles || !styles.props.children.includes(".ptt-root")) throw Error("Missing embedded CSS");
plugin.onDismount();
console.log("Decky runtime smoke test passed: registration, UI tree, bundled CSS.");
