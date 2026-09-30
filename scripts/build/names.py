import json, math, collections
from scipy.spatial import cKDTree
import numpy as np
F=json.load(open('ro_rivers_raw.json'))  # id,next,q,up,len,ordf,ords,coords
byid={}
for f in F: byid.setdefault(f[0],[]).append(f)   # a reach can appear in several parts
parents=collections.defaultdict(list)
for f in F: parents[f[1]].append(f[0])
up={f[0]:f[3] for f in F}; nxt={f[0]:f[1] for f in F}
P=[];I=[]
for f in F:
    if f[3]<300: continue
    for x,y in f[7]: P.append((x,y)); I.append(f[0])
tree=cKDTree(np.array(P)); 
anchors={
 'Dunărea':[(44.71,22.40,570000)],
 'Olt':[(45.10,24.36,15300)],'Mureș':[(46.54,24.55,4100)],'Someș':[(47.14,23.87,8700)],
 'Siret':[(46.10,27.18,22000)],'Prut':[(47.21,27.80,19300)],
 'Jiu':[(45.03,23.27,1450)],'Argeș':[(44.86,24.87,3000)],'Dâmbovița':[(44.43,26.08,2500)],
 'Ialomița':[(44.56,27.38,9200)],'Bistrița':[(46.93,26.38,5400)],'Trotuș':[(46.25,26.77,3900)],
 'Buzău':[(45.15,26.83,3800)],'Timiș':[(45.69,21.90,2900)],'Crișul Alb':[(46.27,22.35,1400)],
 'Arieș':[(46.57,23.78,2350)],'Târnava Mare':[(46.22,24.79,1950)],'Vedea':[(43.97,25.33,3300)],
 'Moldova':[(46.92,26.93,4300)],'Bârlad':[(46.23,27.67,4000)],'Bega':[(45.75,21.23,2100)],
 'Crișul Repede':[(47.05,22.25,1800)],'Someșul Mic':[(46.77,23.6,1200)],'Târnava Mică':[(46.33,24.4,1450)],
}
def stem(rid):
    S={rid}
    # downstream until sibling bigger at confluence
    cur=rid
    while True:
        n=nxt.get(cur,0)
        if not n or n not in up: break
        sib=[p for p in parents[n] if p!=cur]
        if any(up[p]>up[cur] for p in sib): break
        S.add(n); cur=n
    cur=rid
    while True:
        ps=[p for p in parents[cur]]
        if not ps: break
        cur=max(ps,key=lambda p:up[p]); S.add(cur)
    return S
name_of={}
for name,pts in sorted(anchors.items(),key=lambda kv:-kv[1][0][2]):
    S=set()
    for lat,lon,ex in pts:
        idx=tree.query_ball_point((lon,lat),0.09)
        cand=[i for i in idx if 0.5*ex<=up[I[i]]<=2.0*ex]
        if not cand: print(name,'NO CANDIDATE'); continue
        i=min(cand,key=lambda i:abs(math.log(up[I[i]]/ex))); d=math.hypot(P[i][0]-lon,P[i][1]-lat); rid=I[i]
        s=stem(rid); S|=s
        print(f'{name:14s} snap {d*111:5.1f} km up={up[rid]:8.0f} stem={len(s):4d} reaches maxUp={max(up[r] for r in s):8.0f}')
    for r in S:
        if r not in name_of: name_of[r]=(name,r)
json.dump({str(k):v[0] for k,v in name_of.items()},open('names.json','w'),ensure_ascii=False)
print(len(name_of),'named reaches')

import os
os.makedirs('web/data',exist_ok=True)
feats=[]
for f in F:
    rid=f[0]
    props={"i":rid,"q":round(f[2],3),"u":round(f[3],1),"l":round(f[4],2),"o":f[5]}
    if rid in name_of: props["n"]=name_of[rid][0]
    feats.append({"type":"Feature","properties":props,"geometry":{"type":"LineString","coordinates":f[7]}})
json.dump({"type":"FeatureCollection","features":feats},open('web/data/rivers.geojson','w'),separators=(',',':'),ensure_ascii=False)
print(os.path.getsize('web/data/rivers.geojson')/1e6,'MB', len(feats),'features')
