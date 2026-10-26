import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for f in ["OpenSans-Regular.ttf","OpenSans-Bold.ttf","OpenSans-SemiBold.ttf"]: fm.fontManager.addfont("/root/.fonts/"+f)
plt.rcParams.update({"font.family":"Open Sans","font.size":13,"axes.edgecolor":"#8C97A6","axes.labelcolor":"#6E6259","xtick.color":"#6E6259","ytick.color":"#6E6259"})
before=np.array([0,0.5,0,0,0.5,1,0.5,0,0.5,0,0,0.5,0,0.5,0]); after=np.array([1,1,1,1,1,1,1,1,1,0.5,1,1,1,1,0.5])
G={"F":range(0,4),"A":range(4,8),"I":range(8,11),"R":range(11,15)}
lb=[before[list(v)].mean() for v in G.values()]; la=[after[list(v)].mean() for v in G.values()]
pb,pa=np.prod(lb),np.prod(la); print(lb,la,before.mean(),after.mean(),pb,pa,pa/pb)
fig,ax=plt.subplots(1,2,figsize=(10,4.2),gridspec_kw={"width_ratios":[1.15,1]})
x=np.arange(4);w=.38
ax[0].bar(x-w/2,lb,w,color="#8C97A6",label="Before: Drive link + README")
ax[0].bar(x+w/2,la,w,color="#C8102E",label="After: DOI + MIAPPE + Croissant")
for i,(a,b) in enumerate(zip(lb,la)):
    ax[0].text(i-w/2,a+.02,f"{a:.3g}",ha="center",fontsize=11,color="#6E6259"); ax[0].text(i+w/2,b+.02,f"{b:.3g}",ha="center",fontsize=11,color="#222")
ax[0].set_xticks(x,["F","A","I","R"],fontsize=16,fontweight="bold"); ax[0].set_ylim(0,1.45); ax[0].set_ylabel("Letter score"); ax[0].set_yticks([0,.25,.5,.75,1])
ax[0].legend(frameon=False,fontsize=10.5,loc="upper left",ncol=1); ax[0].set_title("Letter scores",color="#1B3A5C",fontweight="bold",fontsize=14)
cb=np.cumprod(lb); ca=np.cumprod(la); L=["F","F·A","F·A·I","F·A·I·R"]
ax[1].plot(L,cb,"o-",color="#8C97A6",lw=2.5,ms=8); ax[1].plot(L,ca,"o-",color="#C8102E",lw=2.5,ms=8)
ax[1].set_yscale("log"); ax[1].set_ylim(1e-3,2)
ax[1].annotate(f"{pb:.4f}",(3,pb),xytext=(-8,-22),textcoords="offset points",ha="right",color="#6E6259",fontsize=12)
ax[1].annotate(f"{pa:.3f}",(3,pa),xytext=(-8,10),textcoords="offset points",ha="right",color="#C8102E",fontsize=12,fontweight="bold")
ax[1].set_title("Weakest-link product (log scale)",color="#1B3A5C",fontweight="bold",fontsize=14)
ax[1].text(1.5,0.004,"280× better",ha="center",fontsize=15,color="#C8102E",fontweight="bold")
for a in ax:
    for s in ["top","right"]: a.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("../../figures/fair_score_chart.png",dpi=200,facecolor="white")
