import json,re,sys
from collections import defaultdict
def norm(s):
    s=re.sub(r"[׳'\"״`’]","",str(s or "").lower()); return re.sub(r"\s+"," ",re.sub(r"[^\w ]"," ",s)).strip()
base=json.load(open(sys.argv[1],encoding='utf-8'))          # clubhub catalog (maybe with L)
ins=json.load(open(sys.argv[2],encoding='utf-8'))           # instinct snapshot
items=base['items']
idx={}
for x in items:
    for a in x.get('a',[x['n']]): idx.setdefault(norm(a),x)
# cross-check stats
inst_biz=set(norm(r['business']) for r in ins['verified_benefits']+ins['wallet_directory_only'])
mine=set(idx)
cover=[b for b in inst_biz if b in mine or any(len(k)>=4 and (k in b or b in k) for k in mine)]
print("instinct unique businesses:",len(inst_biz),"| already in my catalog:",len(cover))
W=defaultdict(list)
for r in ins['wallet_directory_only']: W[r['business'].strip()].append(r)
ONLINE=re.compile(r'(online|אונליין|און ליין|\.co\.il|\.com|אתר|משלוחים)',re.I)
added=0; merged=0
for name,rows in W.items():
    its=[]
    for r in sorted(rows,key=lambda r:-r.get('displayed_wallet_rate_percent',0)):
        fighter='פייטר' in (r.get('wallet_name') or '')
        its.append({"c":"בהצדעה – ארנק","p":f"{r.get('displayed_wallet_rate_percent')}% בטעינת הארנק","d":f"{r.get('wallet_name')} · עד {r.get('monthly_load_limit_ils')} ₪ בחודש"+(" · דורש כרטיס פייטר" if fighter else ""),"u":r.get('source_url'),"b":[],"v":"wallet"})
    # keep one line per wallet name
    seen=set(); its=[i for i in its if not (i['d'] in seen or seen.add(i['d']))]
    k=norm(name); x=idx.get(k)
    if x:
        x['i']+= [i for i in its if i not in x['i']]; merged+=1
    else:
        x={"n":name,"a":[name],"cat":"","i":its,"online":bool(ONLINE.search(name))}
        items.append(x); idx[k]=x; added+=1
for r in ins['verified_benefits']:
    club={'HOT':'הוט'}.get(r['club'],r['club'])
    it={"c":club,"p":r['benefit'][:120],"d":(r.get('terms') or '')[:160],"u":r.get('source_url'),"b":r.get('branches') or [],"v":"verified"}
    k=norm(r['business']); x=idx.get(k)
    if x: x['i'].append(it)
    else:
        x={"n":r['business'],"a":[r['business']],"cat":"","i":[it]}; items.append(x); idx[k]=x
base['updated']=ins['metadata']['snapshot_date']
base['source']="אזור החברים בבהצדעה, 1824 ואתר הוט (דרך Instinct) + clubhub"
json.dump(base,open(sys.argv[3],'w',encoding='utf-8'),ensure_ascii=False)
print("wallet merchants:",len(W),"merged into existing:",merged,"new:",added,"total items:",len(items),"online-only:",sum(1 for x in items if x.get('online')))
