# Opens every hot.co.il benefit page (client-rendered) in a Chrome tab and records whether it is still valid.
import json, re, time, glob, os, sys
from browser_harness import helpers as H
D=os.path.dirname(os.path.abspath(__file__))
EXP=re.compile(r'(פג תוקף|פגה|אינה בתוקף|הסתיימה|לא בתוקף|הדף לא נמצא|העמוד לא נמצא)')
urls=set()
raw=json.load(open(os.path.join(D,'clubhub_raw.json'),encoding='utf-8'))
urls|={i['u'] for x in raw['out'] for i in x['i'] if i['c']=='הוט' and i.get('u')}
snap=sorted(glob.glob(os.path.join(D,'instinct','benefits-snapshot-*.json*')),key=os.path.getmtime)[-1]
ins=json.load(open(snap,encoding='utf-8'))
for k in ('discovery_only','verified_benefits'):
    urls|={r['source_url'] for r in ins.get(k,[]) if r.get('club')=='HOT' and 'hot.co.il' in (r.get('source_url') or '') and r['source_url'].count('/')>=5}
urls=sorted(urls)
res={}
t=H.cdp("Target.createTarget",url="about:blank")["targetId"]
s=H.cdp("Target.attachToTarget",targetId=t,flatten=True)["sessionId"]
def txt():
    try: return H.js("document.body?document.body.innerText:''",target_id=t) or ""
    except Exception: return ""
for n,u in enumerate(urls,1):
    try: H.cdp("Page.navigate",session_id=s,url=u)
    except Exception: pass
    x=""
    for k in range(16):
        time.sleep(0.5); x=txt()
        if "מימוש ההטבה" in x or "פג תוקף" in x or "לא נמצא" in x: break
    time.sleep(1.5); x=txt() or x
    res[u]={"status":200,"has_details":"פרטי ההטבה" in x or "מימוש ההטבה" in x,"expired_words":bool(EXP.search(x))}
    if n%10==0:
        print(n,len(urls),flush=True); json.dump(res,open(os.path.join(D,'hot_check.json'),'w',encoding='utf-8'),ensure_ascii=False)
json.dump(res,open(os.path.join(D,'hot_check.json'),'w',encoding='utf-8'),ensure_ascii=False)
H.cdp("Target.closeTarget",targetId=t)
ok=sum(1 for v in res.values() if v['has_details'] and not v['expired_words'])
print("done",len(urls),"valid",ok,"expired/missing",len(urls)-ok,flush=True)
