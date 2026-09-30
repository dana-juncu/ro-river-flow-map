"""Clip HydroRIVERS to Romania. Big rivers (upland >= 5000 km2) that run ALONG the
border (Danube, Prut, Tisa...) are clipped with a wide buffer so they are not cut
where the coarse outline deviates from the river; small streams use a tight buffer.
Needs: pyshp, shapely; HydroRIVERS shapefile under ./hr ; data/romania.geojson"""
import shapefile, glob, json, time, collections, os
from shapely.geometry import shape, LineString
from shapely.prepared import prep
t=time.time()
ro=shape(json.load(open('web/data/romania.geojson'))['geometry'])
small=ro.buffer(0.06); big=ro.buffer(0.30)
psmall=prep(small); pbig=prep(big)
r=shapefile.Reader(glob.glob('hr/**/*.shp',recursive=True)[0])
feats=[]
for sr in r.iterShapeRecords(bbox=(19.8,43.3,29.9,48.4)):
    rec=sr.record; isbig=rec['UPLAND_SKM']>=5000
    g=LineString(sr.shape.points)
    if not (pbig if isbig else psmall).intersects(g): continue
    c=g.intersection(big if isbig else small)
    if c.is_empty: continue
    parts=[c] if c.geom_type=='LineString' else [p for p in getattr(c,'geoms',[]) if p.geom_type=='LineString']
    for p in parts:
        p=p.simplify(0.0004)
        if p.length<0.001: continue
        feats.append((rec['HYRIV_ID'],rec['NEXT_DOWN'],rec['DIS_AV_CMS'],rec['UPLAND_SKM'],rec['LENGTH_KM'],rec['ORD_FLOW'],rec['ORD_STRA'],[[round(x,4),round(y,4)] for x,y in p.coords]))
print(len(feats),round(time.time()-t,1))
json.dump(feats,open('ro_rivers_raw.json','w'),separators=(',',':'))
print(os.path.getsize('ro_rivers_raw.json')/1e6,'MB')
