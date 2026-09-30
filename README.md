# River Flow Romania

An interactive, animated map of Romania's rivers, lakes and reservoirs. Every river reach is drawn by its average
discharge, and moving dots show the direction of flow. Hover for details, search rivers by name, switch between
English and Romanian. It works on desktop and phone.

**Live map:** https://dana-juncu.github.io/ro-river-flow-map/

> Built with plain HTML/JS and [MapLibre GL JS](https://maplibre.org/). No build step, no API keys.

## What you can do

- **Explore the network:** about 12,000 river reaches, with width and colour scaled by average discharge (m³/s).
- **Hover a river** to highlight the whole river and see its discharge, upstream area and reach length. Named rivers are highlighted end to end.
- **Search** by river name (about 440 names, from the Danube down to mid-sized tributaries such as the Vișeu, Strei or Putna).
- **Filter** with the "show from" slider to hide small streams, and change the animation speed.
- **Lakes and reservoirs:** about 50 of the largest, including Porțile de Fier, Razim–Sinoe, Izvorul Muntelui and Vidraru. Hover for surface area.
- **Toggle** flow animation, river names and terrain relief.
- **"Flow vs 30-day mean" mode:** colours rivers by how today's modelled flow compares with the last 30 days (needs the daily update, see below).

## Where the data comes from

| Layer | Source | Notes |
|---|---|---|
| River network and average discharge | [HydroRIVERS v1.0](https://www.hydrosheds.org/products/hydrorivers) (HydroSHEDS), Europe | ~500 m network; discharge is modelled long-term mean |
| Daily flow ("modelled today") | [GloFAS v4](https://www.globalfloods.eu/) via the [Open-Meteo Flood API](https://open-meteo.com/en/docs/flood-api) | ~5 km grid, only for the larger rivers (≥ 5,000 km² upstream). Non-commercial use only |
| River and lake names, lake outlines | [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors (ODbL) via Overpass | Names matched to HydroRIVERS automatically |
| Country border | [Natural Earth](https://www.naturalearthdata.com/) 10 m | Public domain |
| Terrain shading | Mapzen / AWS terrain tiles (Terrarium) | Loaded live from the internet |

## Read this before using the numbers

- **Discharge is modelled, not measured.** These are not gauge readings and should not be used for flood warnings or engineering decisions. For official data see [INHGA](https://www.inhga.ro/) / [Apele Române](https://rowater.ro/).
- The moving dots show direction and relative size of the flow. Their speed is a visual effect, not a real velocity.
- HydroRIVERS is a ~500 m model. Small streams, canals, the Danube Delta channels and reservoir outlines are approximate, and reach positions can differ from real river courses by a few hundred metres.
- River names are matched to the network automatically, so a few small rivers may be unnamed or wrongly labelled. Corrections and issues are welcome.

## Run it locally

Browsers block a page from loading its own data files when opened by double-click, so serve the folder:

```bash
python -m http.server 8000
# open http://localhost:8000     (on Windows you can double-click serve.bat)
```

## Deploy your own copy (GitHub Pages)

1. Fork or copy this repo.
2. Settings → Pages → Deploy from branch → `main` / root.
3. Optional daily flow: the workflow in `.github/workflows/update-flow.yml` runs `scripts/fetch_flow.py` every morning and commits `data/flow.json`.
   Enable it under Settings → Actions → General → Workflow permissions → **Read and write**, then run it once from the Actions tab.
   Without `data/flow.json` the map simply shows long-term averages.

## Repo layout

```
index.html              the whole app (MapLibre + custom particle canvas)
lib/                    MapLibre GL JS 4.7 (bundled)
data/
  rivers.geojson        river reaches: q (m³/s), u (upstream km²), l (km), o (flow order), n (name), g (group id)
  lakes.geojson         named lakes and reservoirs above 0.5 km²
  romania.geojson       country outline
  flow.json             written daily by the workflow (optional)
scripts/
  fetch_flow.py         daily modelled flow -> data/flow.json
  build/                how the data files were produced (see below)
```

## Rebuilding the data

Only needed if you want to change the extent or refresh names. The scripts need Python with `pyshp`, `shapely`, `scipy`, `numpy`.

1. `prep_ro.py`: clip the HydroRIVERS Europe shapefile (place it in `./hr`) to Romania. Large border rivers such as the Danube keep their full course.
2. `names.py`: names the ~25 main rivers by matching known positions and basin sizes to the network.
3. `osm_names.py`: adds names of medium rivers from an Overpass export (`waterway=river` with `name`) and splits same-named rivers into separate groups.
4. `osm_lakes.py`: builds `lakes.geojson` from an Overpass export of named lakes and reservoirs.

## Credits

**Concept and inspiration:** Thomas Heggelund, creator of the river flow map series on [norway-charts.netlify.app](https://norway-charts.netlify.app/) ([USA](https://norway-charts.netlify.app/river_flow_map_usa/), [Norway](https://norway-charts.netlify.app/river_flow_map/), [Pakistan](https://norway-charts.netlify.app/river_flow_map_pakistan/)). This map applies the same idea to Romania; the code and data pipeline here were written independently.

Data: HydroSHEDS (Lehner & Grill 2013), Copernicus/ECMWF GloFAS via Open-Meteo, OpenStreetMap contributors, Natural Earth, Mapzen/AWS.
Map library: MapLibre GL JS (BSD-3-Clause). Built by Dana Juncu with the help of Claude.

## License

Code: add a license file of your choice (for example MIT). The data files carry the licenses of their sources listed above; `rivers.geojson` and `lakes.geojson` contain OpenStreetMap-derived names and outlines and must keep the "© OpenStreetMap contributors" credit.
