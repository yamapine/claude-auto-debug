# PREREG_SVF_Rotation_20261022.md の判定を機械的に適用する
import sys; sys.path.insert(0,'.')
from load import *
import numpy as np
P=m.pivot(index='ym',columns='idx',values='net').reindex(columns=s.idx).fillna(0.0).sort_index()
P=P.loc['2024-01':'2026-09']
months=list(P.index); EV=[x for x in months if x>='2024-02']
seg=lambda ym: '2024' if ym<'2025' else ('2025' if ym<'2026' else '2026')
base_id=s.groupby(KEY).ngroup().values  # idx順
U={'U1':s.idx[s['filter']=='none'].values,
   'U2':s.idx[s['filter'].isin(['none','atr_pct>=0.12','atr_pct>=0.14','atr_pct>=0.16'])].values}
def rotate(univ,k):
    out={}
    for i,ym in enumerate(months):
        if ym not in EV: continue
        prev=P.iloc[i-1][univ]
        order=prev.sort_values(ascending=False,kind='mergesort')  # 同点はidx昇順（univはidx昇順）
        top=[];seen=set()
        for c in order.index:
            if base_id[c] in seen: continue
            seen.add(base_id[c]); top.append(c)
            if len(top)==k: break
        out[ym]=P.loc[ym,top].mean()
    return pd.Series(out)
def maxdd(r):
    eq=np.concatenate([[0],r.cumsum().values]); return float((np.maximum.accumulate(eq)-eq).max())
def segs(r): return {g:round(v,1) for g,v in r.groupby(r.index.map(seg)).sum().items()}
ref=P.loc[EV,59]; assert s.loc[s.idx==59,'is_ref'].item()==1
print('現行EA設定: 合計',round(ref.sum(),1),segs(ref),'DD',round(maxdd(ref),1))
rng=np.random.default_rng(20261022)
allpass=True
for un,univ in U.items():
    print(f'\n===== {un}（{len(univ)}条件）')
    eqw=P.loc[EV,univ].mean(axis=1); print('参考 全条件等ウェイト: 合計',round(eqw.sum(),1),segs(eqw))
    res={k:rotate(univ,k) for k in (2,3,4,5,6)}
    for k,r in res.items(): print(f' k={k}: 合計 {r.sum():8.1f} {segs(r)} 最悪月 {r.min():7.1f} DD {maxdd(r):6.1f} プラス月 {(r>0).sum()}/{len(r)}')
    r4=res[4]; sg=segs(r4)
    R1=all(v>0 for v in sg.values())
    # R2 ランダム選択
    ub=base_id[univ]; bases=np.unique(ub)
    mem={b:univ[ub==b] for b in bases}
    X=P.loc[:,:]; tot=np.zeros(10000)
    for ym in EV:
        row=P.loc[ym].values
        pick_b=np.argsort(rng.random((10000,len(bases))),axis=1)[:,:4]
        val=np.zeros(10000)
        for j in range(4):
            bsel=bases[pick_b[:,j]]
            ci=np.array([mem[b][rng.integers(len(mem[b]))] for b in bsel])
            val+=row[ci]
        tot+=val/4
    p=((tot>=r4.sum()).sum()+1)/(10000+1)
    R2=p<0.05
    ks=[segs(r) for r in res.values()]
    R3=all(r.sum()>0 for r in res.values()) and all(sum(d[g]>0 for d in ks)>=4 for g in ('2024','2025','2026'))
    R4=maxdd(r4)<=maxdd(ref)
    print(f' ランダム合計: 中央値 {np.median(tot):.1f} / 95%点 {np.percentile(tot,95):.1f} / 実際 {r4.sum():.1f} → p={p:.4f}')
    print(f' 判定 R1={R1} R2={R2} R3={R3} R4={R4}（k=4 DD {maxdd(r4):.1f} vs 現行 {maxdd(ref):.1f}）')
    allpass&=R1 and R2 and R3 and R4
    pd.DataFrame(res).round(3).to_csv(f'rotation_{un}_monthly.csv')
print('\n総合判定:', '合格' if allpass else '不合格')
