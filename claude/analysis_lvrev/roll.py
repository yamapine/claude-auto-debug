import sys; sys.path.insert(0,'.')
from load import *
import numpy as np
P=m.pivot(index='ym',columns='idx',values='net').fillna(0.0).sort_index()
months=list(P.index)
def roll(univ,k=4,lb=1,start='2025-01',end='2026-09'):
    X=P[univ]; res={}
    for i,ym in enumerate(months):
        if ym<start or ym>end: continue
        score=X.iloc[i-lb:i].sum()
        top=score.sort_values(ascending=False,kind='mergesort').index[:k]
        res[ym]=X.iloc[i][top].mean()
    r=pd.Series(res); eq=r.cumsum(); dd=(eq.cummax().clip(lower=0)-eq).max()
    return dict(total=round(r.sum(),1),y2025=round(r[r.index<'2026'].sum(),1),y2026=round(r[r.index>='2026'].sum(),1),
                worst=round(r.min(),1),maxDD=round(dd,1),pos_m=int((r>0).sum()),months=len(r)),r
idx=s.set_index('idx')
U={'F0 全MA(400)':idx[idx['filter']=='none'].index,
   'F0+atr(1600)':idx[idx['filter'].str.match('none|atr')].index,
   '全(5200)':idx.index,
   'F0+lvrev(4000)':idx[idx['filter'].str.match('none|lvrev')].index}
if __name__=='__main__':
    for name,u in U.items():
        for k in (1,2,4):
            print(name,k,roll(list(u),k)[0])
