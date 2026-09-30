# River Flow Romania

An interactive, animated map of Romania's rivers (12,000+ river reaches): line width and colour show average discharge,
dots flow downstream, hover for details, search by river name, lakes and reservoirs, RO/EN toggle, mobile friendly.
Static site: no build step and no API keys.

## Run locally
Browsers block a page from loading its own data files when it is opened by double-click (`file://`), so serve the folder:

    python -m http.server 8000      # then open http://localhost:8000
    (on Windows you can double-click serve.bat)

## Publish on GitHub Pages
1. Put the contents of this folder at the root of a repo (keep `.nojekyll`).
2. Create `.github/workflows/update-flow.yml` from `update-flow.workflow.yml` (optional: daily modelled flow, see below).
3. Settings -> Pages -> Deploy from branch -> `main` / root.

## Daily "modelled flow today" (optional)
`scripts/fetch_flow.py` reads discharge for the larger rivers from the Open-Meteo Flood API (GloFAS v4) and writes
`data/flow.json`; the page picks it up automatically and adds the "now" values and the "flow vs 30-day mean" colouring.
The workflow runs it daily. Needs: Settings -> Actions -> General -> Workflow permissions -> **Read and write**.
Run it once by hand from the Actions tab to create the first `data/flow.json`. Without the file the map shows long-term averages.

## Data files
| File | What |
|---|---|
| `data/rivers.geojson` | HydroRIVERS v1.0 (Europe) clipped to Romania (border rivers keep their full course), simplified. Props: `i` id, `q` mean discharge m3/s, `u` upstream area km2, `l` reach length km, `o` flow order, `n` river name, `g` group id when several distinct rivers share a name |
| `data/lakes.geojson` | Named lakes and reservoirs above 0.5 km2 (OpenStreetMap; a few delta lakes from Natural Earth). Props: `n` name, `a` area km2 |
| `data/romania.geojson` | Country outline (Natural Earth 10m) |
| `data/flow.json` | Optional, written daily by the workflow |

## How the data was built (`scripts/build/`)
1. `prep_ro.py` - clip the HydroRIVERS Europe shapefile to Romania (needs `pyshp`, `shapely`; shapefile in `./hr`).
2. `names.py` - name ~25 main rivers by matching known locations and upstream areas to HydroRIVERS reaches.
3. `osm_names.py` - add names of medium rivers from an OpenStreetMap Overpass export (`waterway=river` + `name`), never overwriting step 2, and split same-named rivers into groups.
4. `osm_lakes.py` - turn an Overpass export of named lakes/reservoirs into `lakes.geojson`.

## Credits and caveats
- Rivers: HydroRIVERS / HydroSHEDS (Lehner & Grill 2013). Long-term discharge from HydroATLAS; daily values GloFAS v4 via Open-Meteo (non-commercial use).
- River and lake names and lake outlines: (c) OpenStreetMap contributors (ODbL). Country border: Natural Earth (public domain). Relief: Mapzen/AWS terrain tiles.
- Map library: MapLibre GL JS (BSD-3-Clause).
- Discharge is modelled, not gauge data. Moving dots show direction and relative size; their speed is not a measured velocity.
- Names are matched automatically; a few small rivers may be unnamed or mislabelled.
