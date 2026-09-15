# -*- coding: utf-8 -*-
import sys,io,os
import numpy as np, cv2
out=[]
for mp4 in sys.argv[1:]:
    cap=cv2.VideoCapture(mp4); fps=cap.get(cv2.CAP_PROP_FPS)
    prev=None; d=[]; picrows=[]
    i=0
    while True:
        ok,f=cap.read()
        if not ok: break
        # 그림 영역만 비교 (제목띠 제외)
        p=f[243:813]
        g=cv2.cvtColor(cv2.resize(p,(152,142)),cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None: d.append((i/fps, float(np.abs(g-prev).mean())))
        prev=g
        # 이 프레임의 그림 세로 범위(레터박스 변화 추적)
        gg=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY); cov=(gg>25).sum(axis=1)/f.shape[1]
        pr=np.where(cov>0.85)[0]
        picrows.append((pr.min(),pr.max()) if len(pr)>100 else (0,0))
        i+=1
    cap.release()
    arr=np.array([x[1] for x in d]); ts=np.array([x[0] for x in d])
    thr=max(12.0, arr.mean()+3*arr.std())
    cut=ts[arr>thr]
    # 0.25s 이내 중복 제거
    keep=[]
    for t in cut:
        if not keep or t-keep[-1]>0.25: keep.append(t)
    dur=i/fps
    out.append("="*72)
    out.append(f"{os.path.basename(mp4)}  {dur:.1f}s  {i}프레임")
    out.append(f"  컷 전환 {len(keep)}회 → 분당 {len(keep)/dur*60:.1f}컷 · 평균 컷 길이 {dur/max(1,len(keep)+1):.2f}s")
    out.append("  전환 시각: "+" ".join(f"{t:.1f}" for t in keep))
    seg=[keep[0]]+[keep[j]-keep[j-1] for j in range(1,len(keep))]+[dur-keep[-1]] if keep else [dur]
    out.append("  컷 길이들: "+" ".join(f"{s:.1f}" for s in seg))
    pr=np.array(picrows)
    uniq=sorted(set(map(tuple,pr[pr[:,1]>0])))
    out.append(f"  그림 세로범위 종류 {len(uniq)}가지 (상위 6): {uniq[:6]}")
io.open("cuts.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
