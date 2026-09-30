#!/usr/bin/env python3
"""Fetch modelled daily river discharge (GloFAS v4 via Open-Meteo) for Romania's larger river reaches
and write data/flow.json:  {"date": "...", "source": "...", "q": {"<HYRIV_ID>": [m3/s today, today / 30-day mean]}}

Design notes
- GloFAS is a 0.05 deg (~5 km) grid. A reach's coordinate can snap to a neighbouring non-river cell, so for each reach
  we query the reach midpoint plus its 4 neighbouring cells and keep the cell whose 30-day mean is closest (log scale)
  to the reach's long-term average discharge (HydroRIVERS DIS_AV_CMS -> property "q" in rivers.geojson).
- Only reaches with upstream area >= MIN_UP km2 are queried (GloFAS is not meaningful for small streams,
  and Open-Meteo's free tier allows 10,000 calls/day; each location counts as a call).
- Non-commercial use of the free API. Attribution: Open-Meteo.com (GloFAS, Copernicus/ECMWF).
"""
import json, math, sys, time, urllib.request, urllib.parse, datetime, pathlib

MIN_UP = 5000.0          # km2
PAST_DAYS = 30
BATCH = 100              # locations per request
STEP = 0.05
ROOT = pathlib.Path(__file__).resolve().parent.parent
API = "https://flood-api.open-meteo.com/v1/flood"

def get(url, tries=5):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:                      # rate limit / transient
            wait = 5 * (k + 1)
            print(f"  retry in {wait}s: {e}", file=sys.stderr); time.sleep(wait)
    raise SystemExit("Open-Meteo request failed; keeping the previous flow.json")

def cell(lat, lon):
    return (round(lat / STEP), round(lon / STEP))

def main():
    fc = json.load(open(ROOT / "data" / "rivers.geojson", encoding="utf-8"))
    reaches = []
    for f in fc["features"]:
        p = f["properties"]
        if p["u"] < MIN_UP: continue
        c = f["geometry"]["coordinates"]; lon, lat = c[len(c) // 2]
        reaches.append((p["i"], p["q"], lat, lon))
    cells = {}
    for _, _, lat, lon in reaches:
        for dy, dx in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            la, lo = lat + dy * STEP, lon + dx * STEP
            cells.setdefault(cell(la, lo), (round(la, 3), round(lo, 3)))
    keys = list(cells)
    print(f"{len(reaches)} reaches, {len(keys)} unique cells")
    series = {}
    for i in range(0, len(keys), BATCH):
        chunk = keys[i:i + BATCH]
        qs = urllib.parse.urlencode({
            "latitude": ",".join(str(cells[k][0]) for k in chunk),
            "longitude": ",".join(str(cells[k][1]) for k in chunk),
            "daily": "river_discharge", "past_days": PAST_DAYS, "forecast_days": 1})
        data = get(f"{API}?{qs}")
        if isinstance(data, dict): data = [data]
        for k, d in zip(chunk, data):
            series[k] = d["daily"]["river_discharge"]; dates = d["daily"]["time"]
        time.sleep(1.0)
    today = dates[-1]
    out = {}
    for rid, qavg, lat, lon in reaches:
        best = None
        for dy, dx in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            s = series.get(cell(lat + dy * STEP, lon + dx * STEP))
            if not s or s[-1] is None: continue
            hist = [v for v in s[:-1] if v is not None]
            if not hist: continue
            m = sum(hist) / len(hist)
            if m < 0.05: continue
            score = abs(math.log(m / max(qavg, 0.05)))
            if best is None or score < best[0]: best = (score, s[-1], m)
        if best and best[0] < 1.6:                  # cell within ~5x of the expected flow
            out[str(rid)] = [round(best[1], 3), round(best[1] / best[2], 2)]
    json.dump({"date": today, "source": "GloFAS v4 via Open-Meteo", "q": out},
              open(ROOT / "data" / "flow.json", "w"), separators=(",", ":"))
    print(f"wrote {len(out)} reaches for {today}")

if __name__ == "__main__":
    main()
