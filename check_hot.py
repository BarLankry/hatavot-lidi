import json, urllib.request, re, sys, time
raw=json.load(open('clubhub_raw.json',encoding='utf-8'))
urls=sorted({i['u'] for x in raw['out'] for i in x['i'] if i['c']=='הוט' and i['u']})
res={}
for u in urls:
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 Chrome/130"}),timeout=15)
        h=r.read().decode('utf-8','ignore'); final=r.geturl()
        exp=bool(re.search(r'(ההטבה אינה בתוקף|ההטבה הסתיימה|ההטבה לא בתוקף|הדף לא נמצא)',h)); ok='פרטי ההטבה' in h
        title=(re.search(r'<title>(.*?)</title>',h,re.S) or [None,''])[1].strip()[:80]
        res[u]={"status":r.status,"final":final,"expired_words":exp,"has_details":ok,"title":title}
    except Exception as e:
        res[u]={"status":getattr(e,'code',0),"err":str(e)[:80]}
    time.sleep(0.4)
json.dump(res,open('hot_check.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
from collections import Counter
print(len(urls), Counter((v.get('status'),v.get('expired_words'),v.get('has_details')) for v in res.values()))
