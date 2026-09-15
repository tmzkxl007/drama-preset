# -*- coding: utf-8 -*-
import re,io,os,sys,glob
def parse(p):
    cues=[];cur=None
    for ln in io.open(p,encoding="utf-8"):
        ln=ln.rstrip("\n")
        m=re.match(r"(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)",ln)
        if m:
            s=lambda t:(lambda h,mi,se:int(h)*3600+int(mi)*60+float(se))(*t.split(":"))
            cur=[s(m.group(1)),s(m.group(2)),[]];cues.append(cur);continue
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
    full=[];prev=""
    for a,b,t in segs:
        add=t[len(prev):].strip() if (prev and t.startswith(prev)) else t
        if add: full.append((a,b,add))
        prev=t
    return full

out=[]
for p in sorted(glob.glob("dl/*.ko.vtt")):
    f=parse(p)
    txt=" ".join(t for _,_,t in f)
    # 원본 대사(») 와 나레이션 분리
    narr=[];dlg=[]
    for a,b,t in f:
        for part in re.split(r"(»)",t):
            pass
    joined=" ".join(t for _,_,t in f)
    parts=re.split(r"\s*»\s*",joined)
    end=f[-1][1]
    ch=len(re.sub(r"[\s»\[\]]|음악","",joined))
    out.append("="*72)
    out.append(f"{os.path.basename(p)}   말 끝 {end:.1f}s")
    out.append(f"  총 글자수 {ch}  → 초당 {ch/end:.1f}자   (한국어 나레 보통 4.5~5.5자/초)")
    out.append(f"  말 덩이 {len(f)}개 · 평균 {end/len(f):.2f}s 마다 새 자막")
    out.append(f"  덩이 글자수: "+" ".join(str(len(re.sub(r'[\s»]','',t))) for _,_,t in f))
    out.append(f"  »(원본대사) 등장 {joined.count('»')}회 · [음악] {joined.count('음악')}회")
    out.append("  첫 3초: "+" ".join(t for a,_,t in f if a<3.5))
    out.append("  마지막 한 덩이: "+f[-1][2])
    # 어미
    ends=re.findall(r"([가-힣]{2,4}(?:고|는데|었고|이었고|하는데|죠|다|지만|되고|인데|더니|버리죠|하며|자))\s",joined+" ")
    out.append("  연결어미 표본: "+", ".join(ends[-12:]))
io.open("cadence.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
