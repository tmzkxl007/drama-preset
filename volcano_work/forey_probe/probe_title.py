# -*- coding: utf-8 -*-
import numpy as np, cv2, io, sys
cap=cv2.VideoCapture(sys.argv[1]); fs=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fs.append(f)
cap.release()
band=np.median(np.stack(fs[::7])[:,:243],axis=0).astype(np.uint8)
g=cv2.cvtColor(band,cv2.COLOR_BGR2GRAY)
ink=(g>90).sum(axis=1)
o=[]
for y in range(band.shape[0]):
    if ink[y]>0:
        m=g[y]>150
        px=band[y][m]
        col=np.median(px,axis=0) if len(px) else [0,0,0]
        o.append(f"y{y:3d} ink{ink[y]:4d}  B{col[0]:5.0f} G{col[1]:5.0f} R{col[2]:5.0f}")
io.open("title_rows.txt","w",encoding="utf-8").write("\n".join(o))
print(len(o))
