# -*- coding: utf-8 -*-
import sys,io,os
import numpy as np, cv2

def grab(mp4,n=90):
    cap=cv2.VideoCapture(mp4); N=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    idxs=np.linspace(0,N-1,n).astype(int); out=[]
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES,int(i)); ok,f=cap.read()
        if ok: out.append((i/fps,f))
    cap.release(); return out,fps,N

out=[]
for mp4 in sys.argv[1:]:
    fs,fps,N=grab(mp4); h,w=fs[0][1].shape[:2]
    out.append("="*72); out.append(f"{os.path.basename(mp4)}  {w}x{h}  {fps:.2f}fps  {N/fps:.1f}s")
    tops=[];bots=[]
    for t,f in fs:
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        cov=(g>25).sum(axis=1)/w          # 행 채움률
        pic=np.where(cov>0.85)[0]         # 그림은 가로 전체가 찬다
        if len(pic)>100: tops.append(pic.min()); bots.append(pic.max())
    tops=np.array(tops);bots=np.array(bots)
    out.append(f"  그림 y {int(np.median(tops))} ~ {int(np.median(bots))}  (높이 {int(np.median(bots))-int(np.median(tops))+1})   상단범위 {tops.min()}-{tops.max()} 하단범위 {bots.min()}-{bots.max()}")
    ytop=int(np.median(tops))

    # 제목: 그림 위쪽 검은 띠 안의 글자
    band=fs[len(fs)//2][1][:ytop]
    g=cv2.cvtColor(band,cv2.COLOR_BGR2GRAY); m=g>100
    rows=np.where(m.sum(axis=1)>2)[0]
    if len(rows):
        gaps=np.where(np.diff(rows)>8)[0]; segs=[];s=rows[0]
        for gi in gaps: segs.append((s,rows[gi])); s=rows[gi+1]
        segs.append((s,rows[-1]))
        for i,(a,b) in enumerate(segs,1):
            sub=band[a:b+1]; mm=cv2.cvtColor(sub,cv2.COLOR_BGR2GRAY)>140
            px=sub[mm]; col=px.mean(axis=0) if len(px) else np.zeros(3)
            cols=np.where(mm.any(axis=0))[0]
            out.append(f"    제목 {i}행: y {a}-{b} 높이 {b-a+1}  x {cols.min()}-{cols.max()} 폭 {cols.max()-cols.min()+1}  BGR({col[0]:.0f},{col[1]:.0f},{col[2]:.0f})")

    # 자막: 그림 영역 안에서 '흰 글자 + 검은 테두리' 가 자주 뜨는 행
    ybot=int(np.median(bots))
    hits=np.zeros(h)
    for t,f in fs:
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        white=(g>225)
        cnt=white.sum(axis=1)
        hits[cnt>12]+=1
    zone=np.where(hits[ytop:ybot]>len(fs)*0.25)[0]+ytop
    if len(zone):
        out.append(f"    자막 잦은 행: y {zone.min()}-{zone.max()}  (프레임의 25% 이상에서 흰 글자)")
    # 자막 있는 프레임 비율
    nsub=0
    for t,f in fs:
        strip=f[int(h*0.55):ybot]
        g=cv2.cvtColor(strip,cv2.COLOR_BGR2GRAY)
        if (g>230).sum()>600: nsub+=1
    out.append(f"    자막 떠 있는 프레임 비율: {nsub}/{len(fs)} = {nsub/len(fs)*100:.0f}%")
io.open("geo2.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
