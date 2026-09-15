# -*- coding: utf-8 -*-
import re,io,sys,os
def parse(p):
    cues=[];cur=None
    for ln in io.open(p,encoding="utf-8"):
        ln=ln.rstrip("\n")
        m=re.match(r"(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)",ln)
        if m:
            def s(t):
                h,mi,se=t.split(":");return int(h)*3600+int(mi)*60+float(se)
            cur=[s(m.group(1)),s(m.group(2)),[]];cues.append(cur);continue
        if cur is not None and ln.strip() and not ln.startswith(("WEBVTT","Kind:","Language:")):
            txt=re.sub(r"<[^>]+>","",ln).strip().replace("&gt;&gt;","»").replace("&gt;",">").replace("&nbsp;"," ")
            if txt: cur[2].append(txt)
    # rolling-caption 정리: 앞 문장이 뒤 문장의 접두어면 뒤 것으로 대체
    segs=[]
    for a,b,ls in cues:
        t=re.sub(r"\s+"," "," ".join(ls)).strip()
        if not t: continue
        if segs and (segs[-1][2]==t): segs[-1][1]=b; continue
        if segs and t.startswith(segs[-1][2]): segs[-1]=[segs[-1][0],b,t]; continue
        segs.append([a,b,t])
    # 증분만 뽑아 전체 대사 복원
    full=[];prev=""
    for a,b,t in segs:
        if t.startswith(prev) and prev:
            add=t[len(prev):].strip()
        else:
            add=t
        if add: full.append((a,b,add))
        prev=t
    return segs,full

out=[]
for p in sys.argv[1:]:
    segs,full=parse(p)
    out.append("="*72)
    out.append(os.path.basename(p)+f"   (자막 끝 {segs[-1][1]:.1f}s)")
    out.append("--- 시간축 (증분) ---")
    for a,b,t in full:
        out.append(f"  {a:6.2f}s  {t}")
    out.append("")
    out.append("--- 전체 대사 이어붙임 ---")
    out.append("  "+" ".join(t for _,_,t in full))
    out.append("")
io.open("narration.txt","w",encoding="utf-8").write("\n".join(out))
print("ok", len(out))
