# -*- coding: utf-8 -*-
import re, io, os, sys, glob, json, statistics as st
sys.stdout.reconfigure(encoding="utf-8")

def parse(p):
    cues=[]; cur=None
    for ln in io.open(p, encoding="utf-8"):
        ln=ln.rstrip("\n")
        m=re.match(r"(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)", ln)
        if m:
            s=lambda t:(lambda h,mi,se:int(h)*3600+int(mi)*60+float(se))(*t.split(":"))
            cur=[s(m.group(1)), s(m.group(2)), []]; cues.append(cur); continue
        if cur is not None and ln.strip() and not ln.startswith(("WEBVTT","Kind:","Language:")):
            t=re.sub(r"<[^>]+>","",ln).strip().replace("&gt;&gt;","»").replace("&gt;",">")
            if t: cur[2].append(t)
    segs=[]
    for a,b,ls in cues:
        t=re.sub(r"\s+"," "," ".join(ls)).strip()
        if not t: continue
        if segs and segs[-1][2]==t: segs[-1][1]=b; continue
        if segs and t.startswith(segs[-1][2]): segs[-1]=[segs[-1][0],b,t]; continue
        segs.append([a,b,t])
    full=[]; prev=""
    for a,b,t in segs:
        add=t[len(prev):].strip() if (prev and t.startswith(prev)) else t
        if add: full.append((a,b,add))
        prev=t
    return full

views=json.load(io.open("views25.json", encoding="utf-8"))
rows=[]
for p in sorted(glob.glob("dl25/*.ko.vtt")):
    vid=os.path.basename(p).split(".")[0]
    f=parse(p)
    if not f: continue
    joined=" ".join(t for _,_,t in f)
    end=f[-1][1]; start=f[0][0]
    clean=lambda s: re.sub(r"[\s»\[\]]|음악","",s)
    ch=len(clean(joined))
    chunks=[len(clean(t)) for _,_,t in f]
    dlg=joined.count("»")                       # 원본 대사 인용 표시
    gaps=[f[i+1][0]-f[i][1] for i in range(len(f)-1)]
    rows.append(dict(id=vid, end=end, start=start, ch=ch, cps=ch/end, n=len(f),
                     chunks=chunks, dlg=dlg, view=views.get(vid,0),
                     gap=st.median(gaps) if gaps else 0))

print("id          조회      말끝  글자  초당자  덩이  덩이중앙  대사»  첫말")
for r in sorted(rows, key=lambda r:-r["view"]):
    print("%-11s %8s %6.1f %5d %6.1f %5d %8d %5d %6.2f" % (
        r["id"], format(r["view"],","), r["end"], r["ch"], r["cps"], r["n"],
        int(st.median(r["chunks"])), r["dlg"], r["start"]))

cps=[r["cps"] for r in rows]
print()
print("초당 글자수   평균 %.2f  중앙 %.2f  범위 %.1f~%.1f" % (st.mean(cps), st.median(cps), min(cps), max(cps)))
ch=[int(st.median(r["chunks"])) for r in rows]
print("자막 덩이     중앙 %d자  전체범위 %d~%d자" % (int(st.median(ch)), min(min(r["chunks"]) for r in rows), max(max(r["chunks"]) for r in rows)))
print("덩이 갈이     중앙 %.2f초마다" % st.median([r["end"]/r["n"] for r in rows]))
print("첫 말 시작    중앙 %.2f초" % st.median([r["start"] for r in rows]))
print("원본대사 인용 중앙 %d회 · 범위 %d~%d회" % (int(st.median([r["dlg"] for r in rows])), min(r["dlg"] for r in rows), max(r["dlg"] for r in rows)))
top=[r for r in rows if r["view"]>=200000]; bot=[r for r in rows if r["view"]<200000]
print()
print("터진편(20만+) %d편  초당 %.2f자" % (len(top), st.mean([r["cps"] for r in top])))
print("안터진편      %d편  초당 %.2f자" % (len(bot), st.mean([r["cps"] for r in bot])))
