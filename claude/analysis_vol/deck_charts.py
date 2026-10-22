# プレゼン用のグラフ画像（スライドの背景色に合わせる）
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
sys.path.insert(0,'../analysis_lvrev'); from load import t
OUT=sys.argv[1]
BG,INK,SUB,BLUE,GOLD,GRAY,GRID='#FBFBF8','#14213D','#4A5568','#2A78D6','#B8860B','#B9B8B2','#E6E4DD'
plt.rcParams.update({'font.family':'IPAGothic','font.size':20,'axes.spines.top':False,'axes.spines.right':False,
 'axes.edgecolor':GRAY,'xtick.color':SUB,'ytick.color':SUB,'axes.labelcolor':SUB})
# 1) 予想 vs 実際
P=pd.read_csv('forecast.csv',index_col=0); P.index=pd.to_datetime(P.index); d=P.loc['2012':]
idx=d.index+pd.offsets.MonthBegin(1)
fig,ax=plt.subplots(figsize=(16.6,6.2),facecolor=BG); ax.set_facecolor(BG)
ax.plot(idx,np.exp(d.y),color=GRAY,lw=2.6,label='実際（来月の1日平均値幅 %）')
ax.plot(idx,np.exp(d.M3),color=BLUE,lw=2.6,label='前の月末の予想（GVZ＋今月の値動き）')
ax.grid(axis='y',color=GRID); ax.set_axisbelow(True); ax.legend(loc='upper left',frameon=False,fontsize=20)
for x,tx in [('2020-03-01','コロナ'),('2025-05-01','関税'),('2026-03-01','最高値→急落')]:
    xx=pd.Timestamp(x); yy=float(np.exp(d.y).reindex(idx).set_axis(idx).asof(xx)) if False else None
for x,y,tx in [('2020-04-01',3.65,'コロナ'),('2025-05-01',2.75,'関税'),('2026-04-01',3.85,'最高値→急落')]:
    ax.text(pd.Timestamp(x),y,tx,ha='center',fontsize=18,color=SUB)
ax.set_ylim(0.6,4.1); fig.tight_layout(); fig.savefig(f'{OUT}/chart_forecast.png',dpi=100,facecolor=BG); plt.close(fig)
# 2) 月次（棒）＋累積
M=pd.read_csv('monthly_vol.csv',index_col=0); M.index=pd.PeriodIndex(M.index,freq='M')
t['ym']=pd.PeriodIndex(t.entry_time.str[:7].str.replace('.','-'),freq='M')
pnl=t[t.in_period==1].groupby('ym').pnl.sum()
q=pd.DataFrame({'g':M.GVZ.shift(1),'p':pnl}).loc['2024-01':'2026-09']; q['p']=q.p.fillna(0); q['off']=q.g<17
x=np.arange(len(q)); lab=[f'{p.year}/{p.month}' if p.month in (1,7) else '' for p in q.index]
fig,(a1,a2)=plt.subplots(2,1,figsize=(16.6,7.4),facecolor=BG,gridspec_kw={'height_ratios':[1,1.1],'hspace':0.18},sharex=True)
for a in (a1,a2):
    a.set_facecolor(BG); a.grid(axis='y',color=GRID); a.set_axisbelow(True)
    for i,o in enumerate(q.off):
        if o: a.axvspan(i-0.5,i+0.5,color='#EEECE4',zorder=0)
a1.bar(x[q.off],q.p[q.off],color=BG,edgecolor='#8A8983',hatch='///',width=0.72,zorder=2)
a1.bar(x[~q.off],q.p[~q.off],color=BLUE,width=0.72,zorder=2); a1.axhline(0,color='#8A8983',lw=1)
a1.legend(handles=[Patch(color=BLUE,label='動かした月'),Patch(facecolor=BG,edgecolor='#8A8983',hatch='///',label='止めた月（前月末GVZ 17未満）')],loc='upper left',frameon=False,fontsize=19)
a1.set_ylabel('月の損益')
c0=q.p.cumsum(); c1=q.p.where(~q.off,0).cumsum()
a2.plot(x,c0,color=GRAY,lw=3,label='ずっと動かす'); a2.plot(x,c1,color=BLUE,lw=3,label='GVZ 17未満の月は止める')
a2.fill_between(x,c0,c1,color=BLUE,alpha=0.10,lw=0); a2.axhline(0,color='#8A8983',lw=1)
a2.legend(loc='upper left',frameon=False,fontsize=19); a2.set_ylabel('累積')
a2.set_xticks(x); a2.set_xticklabels(lab); a2.set_xlim(-0.7,len(q)+2.2)
for c,col in ((c0,SUB),(c1,BLUE)): a2.text(len(q)-0.4,c.iloc[-1],f'{c.iloc[-1]:+,.0f}',va='center',fontsize=20,weight='bold',color=col)
fig.subplots_adjust(left=0.07,right=0.98,top=0.97,bottom=0.08); fig.savefig(f'{OUT}/chart_monthly.png',dpi=100,facecolor=BG)
print('ok')
