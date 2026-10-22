import sys; sys.path.insert(0,".")
from roll import *
base_id=idx.groupby(KEY).ngroup()  # 同一基礎条件（フィルター違い）を1方法として扱う
def roll_distinct(univ,k=4,lb=1,start='2025-01',end='2026-09'):
    X=P[univ]; res={}
    for i,ym in enumerate(months):
        if ym<start or ym>end: continue
        score=X.iloc[i-lb:i].sum().sort_values(ascending=False,kind='mergesort')
        top=[];seen=set()
        for c in score.index:
            b=base_id[c]
            if b in seen: continue
            seen.add(b); top.append(c)
            if len(top)==k: break
        res[ym]=X.iloc[i][top].mean()
    r=pd.Series(res); eq=r.cumsum(); dd=(eq.cummax().clip(lower=0)-eq).max()
    return dict(total=round(r.sum(),1),y2025=round(r[r.index<'2026'].sum(),1),y2026=round(r[r.index>='2026'].sum(),1),worst=round(r.min(),1),maxDD=round(dd,1),pos_m=int((r>0).sum())),r
for name,u in U.items():
    if name.startswith('F0 全'): continue
    for k in (1,2,4): print('distinct',name,k,roll_distinct(list(u),k)[0])
