# PREREG_GoldVol_Forecast_20261022.md の判定を機械的に適用する
import os, numpy as np, pandas as pd
D=os.environ.get('TV_DIR','/root/.claude/uploads/7b8add96-6dec-5806-a6c7-e9425ad304f5/')
rd=lambda f: pd.read_csv(D+f,parse_dates=['time']).set_index('time').sort_index()
x=rd('fbe8b744-OANDA_XAUUSD_1D.csv'); g=rd('88023c88-CBOE_DLY_GVZ_1D.csv'); v=rd('3736e3c0-TVC_VIX_1D.csv')
pc=x.close.shift(1)
tr=(np.maximum(x.high,pc)-np.minimum(x.low,pc))/pc*100
ym=lambda s: s.index.to_period('M')
RV=tr.groupby(ym(tr)).mean(); NRV=tr.groupby(ym(tr)).size()
GVZ=g.close.groupby(ym(g)).last(); VIX=v.close.groupby(ym(v)).last()
M=pd.DataFrame({'RV':RV,'nd':NRV,'GVZ':GVZ,'VIX':VIX}).loc['2008-08':'2026-09']
assert M.isna().sum().sum()==0, M[M.isna().any(axis=1)]
M['y']=np.log(M.RV).shift(-1)  # 来月の log RV
L=np.log(M[['RV','GVZ','VIX']])
X={'M0':[], 'M1':['RV'], 'M2':['GVZ'], 'M3':['RV','GVZ'], 'M4':['RV','GVZ','VIX']}
idx=list(M.index); pred={k:{} for k in X}
for i,t in enumerate(idx):
    if i<36 or pd.isna(M.y.iloc[i]): continue
    tr_=slice(0,i)  # t-1 までの (説明変数, 翌月値) の組 = t 時点で既知
    for k,cols in X.items():
        A=np.column_stack([np.ones(i)]+[L[c].iloc[tr_].values for c in cols])
        b=np.linalg.lstsq(A,M.y.iloc[tr_].values,rcond=None)[0]
        a=np.concatenate([[1],L[cols].iloc[i].values]) if cols else np.array([1.0])
        pred[k][t]=float(a@b)
P=pd.DataFrame(pred); P['y']=M.y.reindex(P.index)
E=P[list(X)].sub(P.y,axis=0)**2
def mse(a,b): return E.loc[a:b].mean()
per={'主評価 2012-23':('2012-01','2023-12'),'2012-15':('2012-01','2015-12'),'2016-19':('2016-01','2019-12'),'2020-23':('2020-01','2023-12'),'参考 2024-26/09':('2024-01','2026-08')}
T=pd.DataFrame({k:mse(*v) for k,v in per.items()}).T
print('MSE（log RV の二乗誤差の平均）'); print(T.round(4).to_string())
m=T.loc['主評価 2012-23']; sub=T.loc[['2012-15','2016-19','2020-23']]
R1=m.M1<m.M0 and (sub.M1<sub.M0).all()
R2=m.M3<=m.M1*0.95 and (sub.M3<sub.M1).sum()>=2
R3=m.M4<=m.M3*0.95 and (sub.M4<sub.M3).sum()>=2
print(f'\nR1 RV={R1}（M1/M0={m.M1/m.M0:.3f}）  R2 GVZ={R2}（M3/M1={m.M3/m.M1:.3f}, サブ勝ち{(sub.M3<sub.M1).sum()}/3）  R3 VIX={R3}（M4/M3={m.M4/m.M3:.3f}, サブ勝ち{(sub.M4<sub.M3).sum()}/3）')
print('M2/M1（GVZ単独 vs RV単独）', round(m.M2/m.M1,3))
# 参考: 高ボラ月の的中
hv=pd.Series({t:np.exp(M.y.iloc[i])>=M.RV.iloc[i-35:i+1].quantile(2/3) for i,t in enumerate(idx) if i>=36 and not pd.isna(M.y.iloc[i])})
th=pd.Series({t:np.log(M.RV.iloc[i-35:i+1].quantile(2/3)) for i,t in enumerate(idx) if i>=36})
for k in ('M1','M3','M4'):
    for a,b,nm in [('2012-01','2023-12','主'),('2024-01','2026-08','参考')]:
        s=(P[k]>=th.reindex(P.index)).loc[a:b]; h=hv.loc[a:b]
        print(f' {k} {nm}: 高ボラ予測 {s.sum()}回 的中率 {(h[s]).mean():.2f} / 実際の高ボラ {h.sum()}回 捕捉率 {(s[h]).mean():.2f}')
M.to_csv('monthly_vol.csv'); P.to_csv('forecast.csv')
