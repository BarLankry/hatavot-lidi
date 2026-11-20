# Adds branch locations to catalog.json using OpenStreetMap Nominatim (1 request/sec).
import json, re, time, sys, os, urllib.request, urllib.parse
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "catalog.json")
CACHE = os.path.join(D, "geocache.json")
UA = "hatavot-lidi/1.0 personal app"
def norm(s):
    s = re.sub(r"[׳'\"״`’]", "", str(s or "").lower())
    return re.sub(r"\s+", " ", re.sub(r"[^\w ]", " ", s)).strip()
try: cache = json.load(open(CACHE, encoding="utf-8"))
except Exception: cache = {}
def search(q, limit=50):
    if q in cache: return cache[q]
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({"q": q, "countrycodes": "il", "format": "jsonv2", "limit": limit, "accept-language": "he"})
    for a in range(3):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20).read())
            break
        except Exception as e:
            time.sleep(3); r = []
    time.sleep(1.1)
    res = [[round(float(x["lat"]), 5), round(float(x["lon"]), 5), x.get("name") or "", x.get("display_name", "")[:80]] for x in r]
    cache[q] = res
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    return res
cat = json.load(open(P, encoding="utf-8"))
GENERIC = {"המטבח", "שבילים", "לבן", "ואהבת", "טעימים", "ריטה", "אותנטי", "המזללה", "מלצרית"}
for n, x in enumerate(cat["items"]):
    if x.get("online"): x["L"] = []; continue
    keys = [k for k in dict.fromkeys(norm(a) for a in x.get("a", [x["n"]])) if len(k) >= 3]
    locs = {}
    for k in keys[:4]:
        for la, lo, name, disp in search(k):
            nn = norm(name)
            if not nn: continue
            if k == nn or (len(k) >= 4 and (k in nn)) or (len(nn) >= 4 and nn in k):
                if k in GENERIC and k != nn: continue
                locs[(la, lo)] = [la, lo, disp]
    for it in x["i"]:
        for b in (it.get("b") or [])[:30]:
            for la, lo, name, disp in search(b, 1):
                locs[(la, lo)] = [la, lo, disp]
    x["L"] = list(locs.values())[:200]
    print(n + 1, len(cat["items"]), x["n"], len(x["L"]), flush=True)
cat["geo"] = time.strftime("%Y-%m-%d")
json.dump(cat, open(P, "w", encoding="utf-8"), ensure_ascii=False)
print("done", sum(1 for x in cat["items"] if x["L"]), "with locations")
