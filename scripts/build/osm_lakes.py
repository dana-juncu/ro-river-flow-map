"""Build data/lakes.geojson from an Overpass dump of named lakes/reservoirs (usage: osm_lakes.py osm_lakes.json out.geojson)"""
import json,sys,math
from shapely.geometry import Polygon,LineString,mapping
from shapely.ops import polygonize,unary_union
d=json.load(open(sys.argv[1])); out=[]
def area_km2(g):
    lat=g.centroid.y; return g.area*111.32*111.32*math.cos(math.radians(lat))
for e in d['elements']:
    t=e['tags']; nm=t.get('name')
    if e['type']=='way':
        pts=[(p['lon'],p['lat']) for p in e['geometry']]
        if len(pts)<4: continue
        g=Polygon(pts).buffer(0)
    else:
        lines=[LineString([(p['lon'],p['lat']) for p in m['geometry']]) for m in e['members'] if m.get('geometry') and len(m['geometry'])>1 and m['role'] in('outer','inner','')]
        polys=list(polygonize(unary_union(lines)))
        if not polys: continue
        g=unary_union(polys).buffer(0)
    g=g.simplify(0.0004)
    a=area_km2(g)
    if a<0.5 or g.is_empty: continue
    out.append({"type":"Feature","properties":{"n":nm,"a":round(a,1)},"geometry":mapping(g)})
    print(f"{nm:35s}{a:8.1f} km2")
json.dump({"type":"FeatureCollection","features":out},open(sys.argv[2],'w'),separators=(',',':'),ensure_ascii=False)
print(len(out))
