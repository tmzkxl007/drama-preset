# -*- coding: utf-8 -*-
"""포레이로 한 편을 통째로 뜯는다. 결과는 편별 dict 로 JSON 에 쌓는다."""
import sys, io, os, json, re, subprocess
import numpy as np, cv2

SCALE = 1920/1080.0   # 608x1080 실측 → 1080x1920 환산

def vtt(p):
    if not os.path.exists(p): return []
    cues=[];cur=None
    for ln in io.open(p,encoding="utf-8"):
        ln=ln.rstrip("\n")
        m=re.match(r"(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)",ln)
        if m:
            s=lambda t:(lambda h,mi,se:int(h)*3600+int(mi)*60+float(se))(*t.split(":"))
            cur=[s(m.group(1)),s(m.group(2)),[]];cues.append(cur);continue
        if cur is not None and ln.strip() and not ln.startswith(("WEBVTT","Kind:","Language:")):
            t=re.sub(r"<[^>]+>","",ln).strip().replace("&gt;&gt;","»").replace("&gt;",">").replace("&amp;","&")
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
        if add: full.append([round(a,2),round(b,2),add])
        prev=t
    return full

def run(mp4):
    vid=os.path.splitext(os.path.basename(mp4))[0]
    cap=cv2.VideoCapture(mp4)
    fps=cap.get(cv2.CAP_PROP_FPS); N=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        frames.append(f)
    cap.release()
    h,w=frames[0].shape[:2]; n=len(frames)
    dur=n/fps
    R={"id":vid,"w":w,"h":h,"fps":round(fps,3),"frames":n,"dur":round(dur,2)}

    # ── 배치: 모든 프레임의 행별 '최대 밝기' → 레터박스는 끝까지 어둡다
    gs=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in frames[::3]]
    stack=np.max(np.stack([g.max(axis=1) for g in gs]),axis=0)   # 행별 전체최대
    lit=np.where(stack>60)[0]
    # 제목 글자도 밝으므로, '가로 채움'으로 다시 확인
    fill=np.max(np.stack([ (g>30).sum(axis=1)/w for g in gs ]),axis=0)
    pic=np.where(fill>0.9)[0]
    ptop,pbot=int(pic.min()),int(pic.max())
    R["pic"]={"top":ptop,"bot":pbot,"h":pbot-ptop+1,
              "top_1920":round(ptop*SCALE),"bot_1920":round(pbot*SCALE),"h_1920":round((pbot-ptop+1)*SCALE),
              "aspect":round(w/(pbot-ptop+1),3)}

    # ── 제목: 그림 위 검은 띠. 정지 텍스트이므로 프레임 중앙값이 깨끗하다
    band=np.median(np.stack(frames[::7])[:, :ptop],axis=0).astype(np.uint8)
    bg=cv2.cvtColor(band,cv2.COLOR_BGR2GRAY)
    ink=(bg>90).sum(axis=1)
    rows=np.where(ink>2)[0]
    lines=[]
    if len(rows):
        gaps=np.where(np.diff(rows)>7)[0]; segs=[];s=rows[0]
        for gi in gaps: segs.append((int(s),int(rows[gi]))); s=rows[gi+1]
        segs.append((int(s),int(rows[-1])))
        for a,b in segs:
            if b-a < 8: continue
            sub=band[a:b+1]; m=cv2.cvtColor(sub,cv2.COLOR_BGR2GRAY)>150
            if m.sum()<40: continue
            px=sub[m]
            col=np.median(px,axis=0)     # BGR
            cols=np.where(m.any(axis=0))[0]
            lines.append({"y":[a,b],"h":b-a+1,"h_1920":round((b-a+1)*SCALE),
                          "x":[int(cols.min()),int(cols.max())],"w":int(cols.max()-cols.min()+1),
                          "w_1920":round((cols.max()-cols.min()+1)*SCALE),
                          "cx":round((cols.min()+cols.max())/2,1),
                          "hex":"#%02X%02X%02X"%(int(round(col[2])),int(round(col[1])),int(round(col[0])))})
    R["title_lines"]=lines
    R["title_band"]={"top":0,"bot":ptop-1,"h":ptop,"h_1920":round(ptop*SCALE)}
    R["bottom_band"]={"top":pbot+1,"bot":h-1,"h":h-1-pbot,"h_1920":round((h-1-pbot)*SCALE)}

    # ── 자막: 그림 안에서 '흰 글자(>=235) 픽셀이 몰린 행'
    capmask=np.zeros((n,),dtype=bool); rowhits=np.zeros(h)
    for i,f in enumerate(frames):
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        wt=(g>=238)
        cnt=wt[ptop:pbot+1].sum(axis=1)
        hot=np.where(cnt>=10)[0]
        if len(hot)>=12:                       # 글자 높이만큼 연속
            capmask[i]=True; rowhits[ptop+hot]+=1
    zone=np.where(rowhits>n*0.05)[0]
    R["caption"]={"on_ratio":round(capmask.sum()/n,3)}
    if len(zone):
        R["caption"].update({"y":[int(zone.min()),int(zone.max())],
                             "y_1920":[round(zone.min()*SCALE),round(zone.max()*SCALE)],
                             "center_1920":round((zone.min()+zone.max())/2*SCALE)})
    # 자막 덩이(연속 구간) 개수·길이
    chunks=[];i=0
    while i<n:
        if capmask[i]:
            j=i
            while j<n and capmask[j]: j+=1
            if (j-i)/fps>0.20: chunks.append([round(i/fps,2),round(j/fps,2)])
            i=j
        else: i+=1
    R["caption"]["chunks"]=len(chunks)
    R["caption"]["chunk_secs"]=[round(b-a,2) for a,b in chunks]

    # ── 컷: 그림 영역만 비교
    small=[cv2.cvtColor(cv2.resize(f[ptop:pbot+1],(152,142)),cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames]
    d=np.array([np.abs(small[i]-small[i-1]).mean() for i in range(1,n)])
    thr=max(12.0, d.mean()+3*d.std())
    idx=np.where(d>thr)[0]+1
    keep=[]
    for i in idx:
        if not keep or (i-keep[-1])/fps>0.25: keep.append(int(i))
    ts=[round(i/fps,2) for i in keep]
    lens=[ts[0]]+[round(ts[k]-ts[k-1],2) for k in range(1,len(ts))]+[round(dur-ts[-1],2)] if ts else [round(dur,2)]
    R["cuts"]={"n":len(ts),"per_min":round(len(ts)/dur*60,1),"times":ts,"lens":lens,
               "avg":round(dur/max(1,len(ts)+1),2),
               "open3s":len([t for t in ts if t<=3.5]),
               "open_lens":[l for l in lens[:6]]}
    # 디졸브인가 하드컷인가 — 스파이크 폭
    wide=0
    for i in keep:
        lo=max(1,i-3);hi=min(len(d),i+3)
        if (d[lo-1:hi-1]>thr*0.45).sum()>=3: wide+=1
    R["cuts"]["soft"]=wide

    # ── 나레이션
    segs=vtt(os.path.splitext(mp4)[0]+".ko.vtt")
    joined=" ".join(s[2] for s in segs)
    clean=re.sub(r"[\[\]»]|음악|박수|웃음","",joined)
    ch=len(re.sub(r"\s","",clean))
    R["narr"]={"segs":len(segs),"chars":ch,"cps":round(ch/dur,2),
               "dlg_marks":joined.count("»"),
               "music_marks":len(re.findall(r"음악",joined)),
               "first":segs[0][2] if segs else "",
               "last":segs[-1][2] if segs else "",
               "end_t":segs[-1][1] if segs else 0,
               "start_t":segs[0][0] if segs else 0,
               "seg_chars":[len(re.sub(r"[\s»]","",s[2])) for s in segs],
               "timeline":segs}
    return R

if __name__=="__main__":
    out=[]
    for p in sys.argv[1:]:
        print("...",os.path.basename(p),flush=True)
        out.append(run(p))
    io.open("analysis.json","w",encoding="utf-8").write(json.dumps(out,ensure_ascii=False,indent=1))
    print("wrote analysis.json")
