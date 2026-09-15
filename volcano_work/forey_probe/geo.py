# -*- coding: utf-8 -*-
import subprocess,sys,io,os,json
import numpy as np, cv2

def frames(mp4, n=60):
    cap=cv2.VideoCapture(mp4)
    N=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    idxs=np.linspace(0,N-1,n).astype(int)
    out=[]
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES,int(i)); ok,f=cap.read()
        if ok: out.append((i/fps,f))
    cap.release(); return out,fps,N

def rowmax(f):  # 각 행의 밝기 최대 (검은 띠 찾기)
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    return g.max(axis=1), g

out=[]
for mp4 in sys.argv[1:]:
    fs,fps,N=frames(mp4)
    h,w=fs[0][1].shape[:2]
    out.append("="*72); out.append(f"{os.path.basename(mp4)}  {w}x{h}  {fps:.2f}fps  {N}f  {N/fps:.1f}s")

    # 그림 영역: 여러 프레임에서 '밝은 행'의 최소/최대
    tops=[];bots=[]
    for t,f in fs:
        rm,g=rowmax(f)
        bright=np.where(rm>40)[0]
        if len(bright)>50: tops.append(bright.min()); bots.append(bright.max())
    tops=np.array(tops);bots=np.array(bots)
    out.append(f"그림 상단 y: 최빈 {np.bincount(tops).argmax()}  범위 {tops.min()}~{tops.max()}")
    out.append(f"그림 하단 y: 최빈 {np.bincount(bots).argmax()}  범위 {bots.min()}~{bots.max()}")

    # 제목 띠: 상단 영역에서 밝은 글자 픽셀의 행 분포
    top=fs[len(fs)//2][1][:int(h*0.25)]
    g=cv2.cvtColor(top,cv2.COLOR_BGR2GRAY)
    ink=(g>110).sum(axis=1)
    rows=np.where(ink>3)[0]
    if len(rows):
        # 두 행으로 쪼개기
        gaps=np.where(np.diff(rows)>6)[0]
        segs=[];s=rows[0]
        for gi in gaps: segs.append((s,rows[gi])); s=rows[gi+1]
        segs.append((s,rows[-1]))
        for i,(a,b) in enumerate(segs,1):
            band=top[a:b+1]; m=cv2.cvtColor(band,cv2.COLOR_BGR2GRAY)>110
            px=band[m]
            col=px.mean(axis=0) if len(px) else np.zeros(3)
            cols=np.where(m.any(axis=0))[0]
            out.append(f"  제목 {i}행: y {a}~{b} (높이 {b-a+1}) x {cols.min()}~{cols.max()} 폭 {cols.max()-cols.min()+1}  BGR평균 ({col[0]:.0f},{col[1]:.0f},{col[2]:.0f})")
    io_out="\n".join(out)
io.open("geo.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
