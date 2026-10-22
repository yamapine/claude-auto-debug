import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'IPAGothic','axes.spines.top':False,'axes.spines.right':False,
 'axes.edgecolor':'#bdbcb6','axes.labelcolor':'#52514e','xtick.color':'#52514e','ytick.color':'#52514e'})
INK,SUB,BLUE,ORANGE,GRAY,RED='#0b0b0b','#52514e','#2a78d6','#eb6834','#bdbcb6','#e34948'
P=pd.read_csv('forecast.csv',index_col=0); P.index=pd.to_datetime(P.index)
fig=plt.figure(figsize=(12,13.5),facecolor='#fcfcfb')
fig.text(0.05,0.965,'金の「荒れ具合」は前もって分かる',fontsize=24,weight='bold',color=INK)
fig.text(0.05,0.935,'カギは GVZ（金の予想変動率）＝ 市場が「これから荒れそう」と見ている度合い',fontsize=14,color=SUB)
# ① 予測 vs 実際
ax=fig.add_axes([0.07,0.63,0.88,0.25],facecolor='#fcfcfb')
d=P.loc['2012':]; idx=d.index+pd.offsets.MonthBegin(1)
ax.plot(idx,np.exp(d.y),color=GRAY,lw=2,label='実際の荒れ具合（来月）')
ax.plot(idx,np.exp(d.M3),color=BLUE,lw=2,label='前の月末の予想（GVZ＋今月の値動き）')
ax.set_ylabel('1日の平均値幅（%）'); ax.grid(axis='y',color='#ebeae6'); ax.set_axisbelow(True)
ax.legend(loc='upper left',frameon=False,fontsize=12)
ax.set_title('① 予想（青）は実際（灰）をよく追いかける',loc='left',fontsize=16,weight='bold',color=INK,pad=10)
for x,t in [('2020-03','コロナ'),('2025-04','関税'),('2026-02','最高値→急落')]:
    xx=pd.Timestamp(x); yy=np.exp(P.y).reindex([xx-pd.offsets.MonthBegin(1)]).max()
    ax.annotate(t,(xx,np.exp(d.y).max()*0.97 if np.isnan(yy) else yy),xytext=(0,8),textcoords='offset points',ha='center',fontsize=11,color=SUB)
# ② GVZ帯と翌月EA
ax2=fig.add_axes([0.07,0.14,0.40,0.36],facecolor='#fcfcfb')
lab=['GVZ 低い\n(11〜16)','GVZ 普通\n(16〜21.5)','GVZ 高い\n(23〜44)']; val=[-36,19,221]; win=['3/11','5/11','8/11']
cols=[GRAY,GRAY,BLUE]
b=ax2.bar(lab,val,color=cols,width=0.55)
for r,v,w in zip(b,val,win):
    ax2.text(r.get_x()+r.get_width()/2,v+(8 if v>=0 else -22),f'{v:+d}',ha='center',fontsize=15,weight='bold',color=INK)
    ax2.text(r.get_x()+r.get_width()/2,-75,f'勝ち月 {w}',ha='center',fontsize=11,color=SUB)
ax2.axhline(0,color='#8a8983',lw=1); ax2.set_ylim(-95,260); ax2.set_yticks([])
ax2.spines['left'].set_visible(False)
ax2.set_title('② 前月末のGVZが高いと\n　 翌月のEAはよく勝つ',loc='left',fontsize=16,weight='bold',color=INK,pad=10)
ax2.text(0,-0.20,'翌月のEA損益の1か月平均（USD）\n現行設定・2024〜26年（参考・事後の集計）',transform=ax2.transAxes,fontsize=10.5,color=SUB)
# ③ どれが当たる
ax3=fig.add_axes([0.58,0.14,0.38,0.36],facecolor='#fcfcfb')
names=['今月の値動き\nだけ','＋ GVZ','＋ GVZ ＋ VIX']; imp=[52,64,62]; c3=[GRAY,BLUE,GRAY]
bb=ax3.barh(names[::-1],imp[::-1],color=c3[::-1],height=0.5)
for r,v in zip(bb,imp[::-1]): ax3.text(v+1.5,r.get_y()+r.get_height()/2,f'{v}%',va='center',fontsize=15,weight='bold',color=INK)
ax3.set_xlim(0,80); ax3.set_xticks([]); ax3.spines['bottom'].set_visible(False)
ax3.tick_params(axis='y',labelsize=13,length=0)
ax3.set_title('③ 予想のハズレがどれだけ減るか\n　（ただの平均で予想した場合と比べて）',loc='left',fontsize=16,weight='bold',color=INK,pad=10)
ax3.text(0,-0.20,'2012〜2023年・144か月で検証（事前に基準を固定）\nGVZを足すと一番よく当たる。VIXは足しても良くならない',transform=ax3.transAxes,fontsize=10.5,color=SUB)
fig.text(0.05,0.578,'つまり：月末にGVZを見て「高い」なら、来月は荒れやすい → EAが稼ぎやすい月',fontsize=15,weight='bold',color=BLUE)
fig.text(0.05,0.015,'※ 全て過去データ（バックテスト値）。②の帯の境目は結果を見て決めたもので、そのまま売買ルールにはしない。',fontsize=10,color=SUB)
out='/home/user/claude-auto-debug/claude/img/GoldVol_explained.png'
import os; os.makedirs(os.path.dirname(out),exist_ok=True); fig.savefig(out,dpi=110,facecolor=fig.get_facecolor()); print(out)
