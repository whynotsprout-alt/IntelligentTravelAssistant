import AMapLoader from "@amap/amap-jsapi-loader";

let loaderPromise: Promise<typeof window.AMap> | null = null;

declare global {
  interface Window {
    AMap: any;
  }
}

export async function ensureAmapLoaded(): Promise<typeof window.AMap> {
  if (window.AMap) return window.AMap;
  if (loaderPromise) return loaderPromise;

  const key = import.meta.env.VITE_AMAP_JS_KEY;
  if (!key) {
    throw new Error("Missing VITE_AMAP_JS_KEY");
  }

  loaderPromise = AMapLoader.load({
    key,
    version: "2.0",
    plugins: ["AMap.Scale", "AMap.ToolBar"],
  }).then(() => window.AMap);

  return loaderPromise;
}
