# 参考（判定に使わない）: 月末に分かる予測ボラと、翌月のEA損益（現行設定・2024〜）
import sys, numpy as np, pandas as pd
sys.path.insert(0,'../analysis_lvrev'); from load import t
P=pd.read_csv('forecast.csv',index_col=0); P.index=pd.PeriodIndex(P.index,freq='M')
M=pd.read_csv('monthly_vol.csv',index_col=0); M.index=pd.PeriodIndex(M.index,freq='M')
t['ym']=pd.PeriodIndex(t.entry_time.str[:7].str.replace('.','-'),freq='M')
pnl=t[t.in_period==1].groupby('ym').pnl.sum()
d=pd.DataFrame({'GVZ月末':M.GVZ,'予測RV(M3)':np.exp(P.M3)}).shift(1)  # 前月末の値で翌月を判断
d['翌月EA損益']=pnl; d=d.dropna().loc['2024-01':'2026-09']
d['帯']=pd.qcut(d['GVZ月末'],3,labels=['GVZ低','GVZ中','GVZ高'])
print(d.groupby('帯',observed=True)['翌月EA損益'].agg(['size',lambda s:(s>0).sum(),'sum','mean']).round(0))
print(d.groupby('帯',observed=True)['GVZ月末'].agg(['min','max']).round(1))
