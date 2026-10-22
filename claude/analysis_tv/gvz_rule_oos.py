# PREREG_TV_GVZRule_OOS_20261022.md の判定を機械的に適用する
import sys, os, numpy as np, pandas as pd
sys.path.insert(0,'.'); from load_tv import tr, D
g=pd.read_csv(D+'88023c88-CBOE_DLY_GVZ_1D.csv',parse_dates=['time']).set_index('time').close
gm=g.groupby(g.index.to_period('M')).last()
mon=tr.groupby('ym').pnl.sum()
df=pd.DataFrame({'pnl':mon,'gvz_prev':gm.shift(1)}).dropna()
def judge(th,a='2008-09',b='2023-12',verbose=True):
    q=df.loc[a:b]; off=q.gvz_prev<th
    tot=q.pnl[off].sum()
    subs={'A':('2008-09','2011-12'),'B':('2012-01','2015-12'),'C':('2016-01','2019-12'),'D':('2020-01','2023-12')}
    rows={}
    for k,(s0,s1) in subs.items():
        qq=q.loc[s0:s1]; o=qq.gvz_prev<th
        rows[k]=dict(止めた月=int(o.sum()),止めた月の合計=round(qq.pnl[o].sum(),1),動かした月の合計=round(qq.pnl[~o].sum(),1),全部動かす=round(qq.pnl.sum(),1))
    S=pd.DataFrame(rows).T
    el=S[S.止めた月>=6]; g2=(el.止めた月の合計<0).mean()>=0.75 if len(el) else False
    rng=np.random.default_rng(20261022); k=int(off.sum()); v=q.pnl.values
    sims=np.array([v[rng.choice(len(v),k,replace=False)].sum() for _ in range(10000)])
    p=((sims<=tot).sum()+1)/10001
    if verbose:
        print(f'境目 {th}: 月数 {len(q)} / 止めた月 {k} / 止めた月の合計 {tot:.1f} / 動かした月の合計 {q.pnl[~off].sum():.1f} / 全部動かす {q.pnl.sum():.1f}')
        print(S.to_string()); print(f'  G1={tot<0}  G2={g2}（対象サブ期間 {len(el)}）  G3 p={p:.4f} → {p<0.05}')
    return tot<0 and g2 and p<0.05
print('===== 判定（境目17）'); ok=judge(17)
print('総合:', '合格' if ok else '不合格')
print('\n===== 参考：境目16 / 18'); judge(16); judge(18)
print('\n===== 参考：GVZ帯ごとの1か月平均（2008-09〜2023-12）')
q=df.loc['2008-09':'2023-12']; band=pd.cut(q.gvz_prev,[0,17,22,999],right=False,labels=['<17','17-22','>=22'])
print(q.groupby(band,observed=True).pnl.agg(['size','mean','sum',lambda s:(s>0).mean()]).round(2))
print('\n===== 参考：2024-01〜2026-10'); judge(17,'2024-01','2026-10')
