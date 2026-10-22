# 参考（事後）: GVZ帯の効果が現行設定だけか、全条件で共通かを確認
import sys, numpy as np, pandas as pd
sys.path.insert(0,'../analysis_lvrev'); from load import s, m
M=pd.read_csv('monthly_vol.csv',index_col=0)
P=m.pivot(index='ym',columns='idx',values='net').fillna(0.0).loc['2024-01':'2026-09']
g=M.GVZ.shift(1).reindex(P.index)
band=pd.cut(g,[0,17,22,99],labels=['<17','17-22','>=22'],right=False)
for nm,f in [('F0(400)',s['filter']=='none'),('全5200',s['filter'].notna())]:
    ids=s.idx[f].values; X=P[ids]
    mean=X.groupby(band.values,observed=True).mean()
    print(f'\n{nm}: 帯ごとの1か月平均損益（条件の中央値） ', mean.median(axis=1).round(1).to_dict(), ' 月数',band.value_counts().to_dict())
    print('  高(>=22) > 低(<17) の条件の割合', round((mean.loc['>=22']>mean.loc['<17']).mean()*100,1),'%')
    print('  低(<17)の月の合計がマイナス（＝止めると得）の条件の割合', round((X[band=='<17'].sum()<0).mean()*100,1),'%')
    print('  高(>=22)の月の合計がプラスの条件の割合', round((X[band=='>=22'].sum()>0).mean()*100,1),'%')
    for v in ['V1','V2','V3','V4']:
        ii=s.idx[f&(s.variant==v)].values
        print(f'   {v}: 低<17で損 {(X[ii][band=="<17"].sum()<0).mean()*100:.0f}% / 高>=22でプラス {(X[ii][band==">=22"].sum()>0).mean()*100:.0f}%')
