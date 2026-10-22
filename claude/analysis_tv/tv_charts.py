# TV 20年データのプレゼン用グラフ
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'.'); from load_tv import tr, D
OUT=sys.argv[1]
BG,INK,SUB,BLUE,GRAY,GRID,DGRAY='#FBFBF8','#14213D','#4A5568','#2A78D6','#B9B8B2','#E6E4DD','#8A8983'
plt.rcParams.update({'font.family':'IPAGothic','font.size':20,'axes.spines.top':False,'axes.spines.right':False,
 'axes.edgecolor':GRAY,'xtick.color':SUB,'ytick.color':SUB,'axes.labelcolor':SUB})
# 1) 累積損益（月次）
m=tr.groupby('ym').pnl.sum().sort_index(); c=m.cumsum(); x=m.index.to_timestamp()
fig,ax=plt.subplots(figsize=(16.6,6.0),facecolor=BG); ax.set_facecolor(BG)
pre=x<pd.Timestamp('2026-01-01')
ax.plot(x[pre],c[pre],color=DGRAY,lw=3); ax.plot(x[~pre|(x==x[pre][-1])],c[~pre|(x==x[pre][-1])],color=BLUE,lw=3.5)
ax.axhline(0,color=DGRAY,lw=1); ax.grid(axis='y',color=GRID); ax.set_axisbelow(True)
lo=c.loc[:'2025-12'].idxmin(); ax.annotate(f'2025年末 {c.loc["2025-12"]:+,.0f}',(pd.Timestamp('2025-12-01'),c.loc['2025-12']),xytext=(pd.Timestamp('2017-06-01'),-4600),
  fontsize=21,color=INK,arrowprops=dict(arrowstyle='->',color=DGRAY))
ax.annotate(f'2026年だけで {m.loc["2026-01":].sum():+,.0f}',(pd.Timestamp('2026-09-01'),c.iloc[-1]),xytext=(pd.Timestamp('2019-01-01'),-900),
  fontsize=21,color=BLUE,weight='bold',arrowprops=dict(arrowstyle='->',color=BLUE))
ax.set_ylabel('累積損益（USD/oz）'); ax.set_ylim(-5300,800)
fig.tight_layout(); fig.savefig(f'{OUT}/tv_cum.png',dpi=100,facecolor=BG); plt.close(fig)
# 2) 年ごとの損益
y=tr.groupby('y').pnl.sum()
fig,ax=plt.subplots(figsize=(16.6,6.0),facecolor=BG); ax.set_facecolor(BG)
cols=[BLUE if v>0 else GRAY for v in y.values]
ax.bar(y.index,y.clip(upper=700).values,color=cols,width=0.72,zorder=2)
ax.axhline(0,color=DGRAY,lw=1); ax.grid(axis='y',color=GRID); ax.set_axisbelow(True)
for yr,v in y.items():
    if v>0: ax.text(yr,min(v,700)+20,f'+{v:,.0f}',ha='center',fontsize=18,color=BLUE,weight='bold')
ax.text(2025.4,640,'2026年の棒は途中で切っています →',ha='right',va='center',fontsize=16,color=SUB)
ax.set_xticks(range(2006,2027,2)); ax.set_ylim(-720,800); ax.set_ylabel('年間損益（USD/oz）')
ax.text(2006,560,'2006〜2024年：19年中18年がマイナス（2010年は −1）',ha='left',fontsize=21,color=INK)
fig.tight_layout(); fig.savefig(f'{OUT}/tv_annual.png',dpi=100,facecolor=BG); plt.close(fig)
# 3) GVZ帯ごとの1か月平均（2008-09〜2023-12）
g=pd.read_csv(D+'88023c88-CBOE_DLY_GVZ_1D.csv',parse_dates=['time']).set_index('time').close
gm=g.groupby(g.index.to_period('M')).last().shift(1)
q=pd.DataFrame({'p':m,'g':gm}).dropna().loc['2008-09':'2023-12']
b=pd.cut(q.g,[0,17,22,999],right=False,labels=['GVZ 17未満\n（休む予定だった月）','GVZ 17〜22','GVZ 22以上\n（荒れた月）'])
r=q.groupby(b,observed=True).p.agg(['mean','size',lambda s:(s>0).mean()*100])
fig,ax=plt.subplots(figsize=(11.6,6.4),facecolor=BG); ax.set_facecolor(BG)
bars=ax.bar(range(3),r['mean'],color=[GRAY,GRAY,'#C0504D'],width=0.55,zorder=2)
ax.axhline(0,color=DGRAY,lw=1); ax.grid(axis='y',color=GRID); ax.set_axisbelow(True)
for i,(mv,n,w) in enumerate(r.values):
    ax.text(i,mv-3,f'{mv:+.0f}',ha='center',va='top',fontsize=26,weight='bold',color=INK)
    ax.text(i,4,f'{int(n)}か月・勝ち月{w:.0f}%',ha='center',va='bottom',fontsize=17,color=SUB)
ax.set_xticks(range(3)); ax.set_xticklabels(r.index,fontsize=19); ax.set_ylim(-60,14)
ax.set_ylabel('翌月の1か月平均損益')
fig.tight_layout(); fig.savefig(f'{OUT}/tv_gvz_band.png',dpi=100,facecolor=BG); plt.close(fig)
print(r.round(1)); print('ok')
