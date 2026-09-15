# -*- coding: utf-8 -*-
import subprocess,numpy as np,io,sys,os
out=[]
for mp4 in sys.argv[1:]:
    raw=subprocess.run(["ffmpeg","-v","error","-i",mp4,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
    x=np.frombuffer(raw,dtype=np.int16).astype(np.float32)/32768
    sr=16000; win=int(sr*0.1)
    n=len(x)//win
    rms=np.array([np.sqrt((x[i*win:(i+1)*win]**2).mean()+1e-12) for i in range(n)])
    db=20*np.log10(rms+1e-9)
    out.append("="*72); out.append(f"{os.path.basename(mp4)}  {len(x)/sr:.1f}s")
    out.append(f"  RMS dB: 중앙 {np.median(db):.1f} · 하위10% {np.percentile(db,10):.1f} · 상위10% {np.percentile(db,90):.1f}")
    sil=(db<-45).sum()/n*100
    out.append(f"  무음(-45dB 이하) 비율 {sil:.1f}%  → 소리가 끊기지 않는다면 0에 가깝다")
    # 0.1초 단위 레벨 스파크라인
    lv=np.clip(((db+60)/50*8).astype(int),0,8)
    bars="▁▂▃▄▅▆▇██"
    out.append("  레벨: "+"".join(bars[v] for v in lv))
io.open("audio.txt","w",encoding="utf-8").write("\n".join(out))
print("ok")
