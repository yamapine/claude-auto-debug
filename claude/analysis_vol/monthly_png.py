# 月ごとの解説図: 前月末GVZ / 月次損益（停止した月を区別）/ 累積損益
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
sys.path.insert(0,'../analysis_lvrev'); from load import t
plt.rcParams.update({'font.family':'IPAGothic','axes.spines.top':False,'axes.spines.right':False,
 'axes.edgecolor':'#bdbcb6','xtick.color':'#52514e','ytick.color':'#52514e'})
INK,SUB,BLUE,GRAY,GRID,BG='#0b0b0b','#52514e','#2a78d6','#bdbcb6','#ebeae6','#fcfcfb'
M=pd.read_csv('monthly_vol.csv',index_col=0); M.index=pd.PeriodIndex(M.index,freq='M')
t['ym']=pd.PeriodIndex(t.entry_time.str[:7].str.replace('.','-'),freq='M')
pnl=t[t.in_period==1].groupby('ym').pnl.sum()
d=pd.DataFrame({'g':M.GVZ.shift(1),'p':pnl}).loc['2024-01':'2026-09']; d['p']=d.p.fillna(0)
TH=17; d['off']=d.g<TH; d['rule']=d.p.where(~d.off,0)
x=np.arange(len(d)); lab=[f'{p.year%100:02d}/{p.month}' if p.month in (1,4,7,10) else '' for p in d.index]
fig,axs=plt.subplots(3,1,figsize=(13,14),facecolor=BG,gridspec_kw={'height_ratios':[1,1.5,1.3],'hspace':0.42})
fig.subplots_adjust(top=0.875,bottom=0.07,left=0.08,right=0.97)
fig.text(0.05,0.955,'「GVZが低い月はEAを止める」を月ごとに見る',fontsize=23,weight='bold',color=INK)
fig.text(0.05,0.925,'現行EA設定・2024年1月〜2026年9月（33か月）・金1オンスあたりの損益（バックテスト値・事後の当てはめ）',fontsize=12.5,color=SUB)
def shade(ax):
    for i,o in enumerate(d.off):
        if o: ax.axvspan(i-0.5,i+0.5,color='#f1f0ec',zorder=0)
    for b in (12,24): ax.axvline(b-0.5,color='#d6d5cf',lw=1,zorder=0)
for ax in axs:
    ax.set_facecolor(BG); shade(ax); ax.set_xticks(x); ax.set_xticklabels(lab,fontsize=11); ax.set_xlim(-0.7,len(d)+1.6)
    ax.grid(axis='y',color=GRID); ax.set_axisbelow(True)
    for i,y in ((5.5,'2024年'),(17.5,'2025年'),(28,'2026年')): ax.text(i,1.02,y,transform=ax.get_xaxis_transform(),ha='center',fontsize=12,color=SUB)
# ① GVZ
a=axs[0]; a.plot(x,d.g,color=BLUE,lw=2,marker='o',ms=5,zorder=3)
a.axhline(TH,color='#8a8983',lw=1.5,ls='--'); a.text(len(d)-0.4,TH+0.6,'17 = 停止ライン',ha='right',fontsize=11,color=SUB)
a.set_title('① 前月末のGVZ（灰色の帯＝17未満なので、その月はEAを止めた）',loc='left',fontsize=15,weight='bold',color=INK,pad=22)
# ② 月次損益
a=axs[1]
a.bar(x[d.off],d.p[d.off],color='white',edgecolor='#8a8983',hatch='///',lw=1,width=0.72,zorder=2)
a.bar(x[~d.off],d.p[~d.off],color=BLUE,width=0.72,zorder=2)
a.axhline(0,color='#8a8983',lw=1)
for i in np.argsort(-d.p.values)[:3]: a.text(i,d.p.iloc[i]+15,f'+{d.p.iloc[i]:.0f}',ha='center',fontsize=10.5,color=INK)
a.legend(handles=[Patch(color=BLUE,label='動かした月の損益'),Patch(facecolor='white',edgecolor='#8a8983',hatch='///',label='止めた月（この損益を避けた）')],loc='upper left',frameon=False,fontsize=11.5)
a.set_title('② 月ごとの損益：止めた13か月は、10か月が負けていた月',loc='left',fontsize=15,weight='bold',color=INK,pad=22)
s=d.p[d.off]; a.text(0.99,0.95,f'止めた月の合計 {s.sum():+.0f}\n（負け {int((s<0).sum())}／{len(s)}か月）',transform=a.transAxes,ha='right',va='top',fontsize=12,color=INK,
    bbox=dict(boxstyle='round,pad=0.5',fc='white',ec='#d6d5cf'))
# ③ 累積
a=axs[2]; c0=d.p.cumsum(); c1=d.rule.cumsum()
a.plot(x,c0,color=GRAY,lw=2.5,label='ずっと動かした場合'); a.plot(x,c1,color=BLUE,lw=2.5,label='GVZ 17未満の月は止めた場合')
a.fill_between(x,c0,c1,where=c1>=c0,color=BLUE,alpha=0.10,lw=0)
a.axhline(0,color='#8a8983',lw=1); a.legend(loc='upper left',frameon=False,fontsize=11.5)
for c,col in ((c0,SUB),(c1,BLUE)): a.text(len(d)-0.6,c.iloc[-1],f' {c.iloc[-1]:+,.0f}',va='center',ha='left',fontsize=12,weight='bold',color=col,
    bbox=dict(boxstyle='round,pad=0.2',fc=BG,ec='none'))
i24=11; a.annotate(f'2025年末まで\n止めない: {c0.iloc[23]:+.0f}\n止める: {c1.iloc[23]:+.0f}',(23,c1.iloc[23]),xytext=(15.5,c1.max()*0.42),fontsize=11.5,color=INK,
    arrowprops=dict(arrowstyle='->',color='#8a8983'),bbox=dict(boxstyle='round,pad=0.5',fc='white',ec='#d6d5cf'))
a.set_title('③ 累積の損益：差がつくのは2024〜25年（2026年は一度も止めていない）',loc='left',fontsize=15,weight='bold',color=INK,pad=22)
fig.text(0.05,0.02,'※ 境目17は結果を見てから決めた目安。月の損益は建玉した月で集計。止めた月の損益は0として累積。',fontsize=10.5,color=SUB)
out='/home/user/claude-auto-debug/claude/img/GVZ_stop_rule_monthly.png'; fig.savefig(out,dpi=105,facecolor=BG); print(out)
print(d.assign(p=d.p.round(0),g=d.g.round(1)).to_string())
