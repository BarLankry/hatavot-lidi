# Rebuild catalog.json from: verified HOT pages (clubhub list + hot.co.il check), Instinct snapshot, Isracard GiftCard list.
import json, re, sys, os, glob
D=os.path.dirname(os.path.abspath(__file__))
def J(p): return json.load(open(os.path.join(D,p),encoding='utf-8'))
def norm(s):
    s=re.sub(r"[׳'\"״`’]","",str(s or "").lower()); return re.sub(r"\s+"," ",re.sub(r"[^\w ]"," ",s)).strip()
old={x['n']:x for x in J('catalog.json')['items']}
snap=sorted(glob.glob(os.path.join(D,'instinct','benefits-snapshot-*.json*')),key=os.path.getmtime)[-1]
ins=json.load(open(snap,encoding='utf-8'))
items=[]; idx={}
def get(name,aliases=()):
    k=norm(name)
    if k in idx: return idx[k]
    x={"n":name.strip(),"a":sorted({name.strip(),*aliases}),"cat":"","i":[]}
    o=old.get(x["n"])
    if o:
        x["a"]=sorted(set(x["a"])|set(o.get("a",[]))); 
        if "L" in o: x["L"]=o["L"]
        if o.get("cat"): x["cat"]=o["cat"]
    items.append(x); idx[k]=x
    for a in x["a"]: idx.setdefault(norm(a),x)
    return x
# 1) HOT – only pages that are live on hot.co.il today
raw=J('clubhub_raw.json'); chk=J('hot_check.json')
hot_ok=hot_bad=0
for d in raw['out']:
    for it in d['i']:
        if it['c']!='הוט': continue
        c=chk.get(it['u'],{})
        if c.get('status')==200 and c.get('has_details') and not c.get('expired_words'):
            x=get(d['n']); x['i'].append({"c":"הוט","p":it['p'],"d":it['d'] if it['d']!=d['n'] else "","u":it['u'],"b":it['b'],"v":"verified"})
            if it.get('img') and not x.get('img'): x['img']=it['img']
            if it.get('cat') and not x['cat']: x['cat']=it['cat']
            hot_ok+=1
        else: hot_bad+=1
# 2) Behatsdaa wallets (signed-in directory, today)
ONLINE=re.compile(r'(online|אונליין|און ליין|\.co\.il|\.com|משלוחים)',re.I)
for r in ins['wallet_directory_only']:
    x=get(r['business'])
    fighter='פייטר' in (r.get('wallet_name') or '')
    line={"c":"בהצדעה – ארנק","p":f"{r.get('displayed_wallet_rate_percent')}% בטעינת הארנק","d":f"{r.get('wallet_name')} · עד {r.get('monthly_load_limit_ils')} ₪ בחודש"+(" · דורש כרטיס פייטר" if fighter else ""),"u":r.get('source_url'),"b":[],"v":"wallet"}
    if line not in x['i']: x['i'].append(line)
    if 'מסעדות' in (r.get('wallet_name') or '') and not x['cat']: x['cat']='מסעדה'
    if ONLINE.search(x['n']): x['online']=True
# 3) verified detail pages (Instinct)
for r in ins['verified_benefits']:
    club={'HOT':'הוט'}.get(r['club'],r['club'])
    x=get(r['business']); x['i'].append({"c":club,"p":r['benefit'][:140],"d":(r.get('terms') or '')[:180],"u":r.get('source_url'),"b":[b if isinstance(b,str) else (b.get('name') or b.get('city') or b.get('address') or '') for b in (r.get('branches') or [])],"v":"verified"})
# 4) coupons / specific offers seen today on the signed-in sites (not expired per source)
cp=0
for r in ins['discovery_only']:
    if r.get('source_reported_expired') or not r.get('benefit'): continue
    if r['club']=='HOT' and 'hot.co.il' in (r.get('source_url') or ''):
        c=chk.get(r['source_url'])
        if not c or not c.get('has_details') or c.get('expired_words'): continue
    club={'HOT':'הוט'}.get(r['club'],r['club'])
    items.append({"n":r['business'],"a":[],"cat":(r.get('category') or '').replace(' NOVEMBER SALE','').strip() or "מבצעים","coupon":True,
                  "i":[{"c":club,"p":r['benefit'],"d":r.get('location_headline') or '',"u":r.get('source_url'),"b":[],"v":"discovery"}]}); cp+=1
# 5) Isracard GiftCard (payment method, partial public list)
GIFT="ויקטורי, יינות ביתן, מגה בעיר, מחסני השוק, היפר כהן, זול ובגדול, כמעט חינם, טיב טעם, חצי חינם, יוחננוף, מחסני להב, פרשמרקט, סופר דוש, סופר ברקת, שוק העיר, AM:PM, סטופמרקט, קואופ שופ, אלונית, שוק מהדרין, טומי הילפיגר, נאוטיקה, רנואר, טימברלנד, אמריקן איגל, דפנה לוינסון, קסטרו, ג'אמפ, גולף, בילבונג, הגרה, לי קופר, עדיקה, ריפליי, מייקל קורס, ליוויס, לקוסט, קלווין קליין, פולו ראלף לורן, הוגו בוס, עונות, פולגת, גולברי, ביג שופ, תיק התיקים, מאסימו דוטי, Razili, Lefties, Offline, CALL IT SPRING, FOX, LONGCHAMP, PULL&BEAR, ZARA, Crazy Line, Bershka, SUPERDRY, MANGO, Desigual, H&O, Twentyfourseven, Armani, Inter Jeans, Stradivarius, Factory 54, FIX, aerie, דלתא, אינטימה, דונה ויקטוריה, ליידי קומפורט, אלדו, ניין ווסט, גלי, כל נעל, STEVE MADDEN, Asics, GET PRO, אלוף ספורט, מגה ספורט, רוזן ומינץ, למטייל, סטימצקי, צומת ספרים, The Children's Place, גולף קידס, נמרוד, עגליס, שילב, המשביר לצרכן, ACE, אירופלקס, הולנדיה, AHAVA, SABON, איב רושה, בודי שופ, ללין, פארמה נייס, גולף אנד קו, ZARA HOME, FOX HOME, כיתן, ורדינון, נעמן, yard & co, SOHO, טולמנס, סולתם, סיטי שופ, ארקוסטיל, רויאלטי, ה. שטרן, הבורסה לתכשיטים, מילר, TOUS, אימפרס, Sunglass Hut, אופטיקנה, אופטיקה הלפרין, אייבורי, באג, דינמיקה, מחסני תאורה, טרקלין חשמל, שקם אלקטריק, סינמטק ירושלים"
for g in [s.strip() for s in GIFT.split(",") if s.strip()]:
    x=get(g); x['i'].append({"c":"גיפט קארד ישראכרט","p":"אפשר לשלם בכרטיס המתנה","d":"לפי רשימה חלקית של ישראכרט – הרשימה משתנה","u":"https://digital.isracard.co.il/link/9724cf833776493697fcddeb9312e2e2.aspx","b":[],"v":"gift"})
cat={"updated":ins['metadata']['snapshot_date'],"source":"אזור החברים בבהצדעה ו-1824 (דרך Instinct), אתר הוט (נבדק שההטבה פעילה), ישראכרט","items":[x for x in items if x['i']]}
json.dump(cat,open(os.path.join(D,'catalog.json'),'w',encoding='utf-8'),ensure_ascii=False)
print("items",len(cat['items']),"hot ok",hot_ok,"hot dropped",hot_bad,"coupons",cp,"with L",sum(1 for x in cat['items'] if x.get('L')))
