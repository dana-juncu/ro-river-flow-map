"""Add names of medium-sized rivers from OpenStreetMap (waterway=river, name=*) to
rivers.geojson. Existing hand-matched names are never overwritten.
Usage: python osm_names.py osm_rivers.json web/data/rivers.geojson"""
import json, sys, re, math, collections
import numpy as np
from scipy.spatial import cKDTree
osm, gj = sys.argv[1], sys.argv[2]
TOL=0.006      # ~500 m: HydroRIVERS is derived from a ~500 m grid
MIN_UP=20      # km2 upstream: skip tiny streams
SHARE=0.55     # share of a reach's points that must sit on the OSM line
def clean(n):
    n=n.split(' - ')[0].split(' / ')[0].strip()
    n=re.sub(r'^(Râul|Râu|Raul|Pârâul|Paraul|Valea|Canalul)\s+','',n)
    return n[:1].upper()+n[1:]
def dens(pts,step=0.0012):
    out=[]
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        n=max(1,int(math.hypot(x1-x0,y1-y0)/step))
        out+=[(x0+(x1-x0)*i/n,y0+(y1-y0)*i/n) for i in range(n)]
    out.append(pts[-1]); return out
d=json.load(open(osm))
P=[];N=[]
for e in d['elements']:
    if e['type']!='way' or 'geometry' not in e: continue
    nm=clean(e['tags']['name'])
    if nm in('Dunărea','Dunare','Mare','Mică','Nou','Vechi') or not re.match(r'^[A-Za-zĂÂÎȘŞȚŢăâîșşțţéíóöüőű\- .()]+$',nm): continue
    pts=[(g['lon'],g['lat']) for g in e['geometry']]
    for p in dens(pts): P.append(p); N.append(nm)
tree=cKDTree(np.array(P))
fc=json.load(open(gj))
added=collections.Counter(); 
for f in fc['features']:
    pr=f['properties']
    if 'n' in pr or pr['u']<MIN_UP: continue
    pts=dens(f['geometry']['coordinates'],0.002)
    dist,idx=tree.query(np.array(pts),distance_upper_bound=TOL)
    votes=collections.Counter(N[i] for dd,i in zip(dist,idx) if dd<=TOL)
    if not votes: continue
    nm,c=votes.most_common(1)[0]
    if c/len(pts)>=SHARE:
        pr['n']=nm; added[nm]+=1
json.dump(fc,open(gj,'w'),separators=(',',':'),ensure_ascii=False)
print(len(added),'new river names on',sum(added.values()),'reaches')
print(added.most_common(80))

# --- disambiguate homonyms: same name, spatially separate rivers get their own group id "g"
from scipy.cluster.hierarchy import fcluster, linkage
byn=collections.defaultdict(list)
for f in fc['features']:
    if 'n' in f['properties']: byn[f['properties']['n']].append(f)
for nm,fs in byn.items():
    if len(fs)<2: continue
    # single-linkage over reach bounding-box centres + endpoints
    pts=[]; own=[]
    for i,f in enumerate(fs):
        c=f['geometry']['coordinates']
        for p in (c[0],c[-1]): pts.append(p); own.append(i)
    tr=cKDTree(np.array(pts)); par=list(range(len(fs)))
    def find(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for a,b in tr.query_pairs(0.07): par[find(own[a])]=find(own[b])
    roots=sorted({find(i) for i in range(len(fs))}, key=lambda r:-sum(1 for i in range(len(fs)) if find(i)==r))
    if len(roots)>1:
        for i,f in enumerate(fs): f['properties']['g']=f"{nm}#{roots.index(find(i))+1}"
json.dump(fc,open(gj,'w'),separators=(',',':'),ensure_ascii=False)
print('homonym groups split:',sum(1 for fs in byn.values() if any('g' in f['properties'] for f in fs)))
