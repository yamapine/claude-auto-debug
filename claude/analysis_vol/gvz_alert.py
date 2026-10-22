# PREREG_GVZ_Alert_20261022.md の判定を機械的に適用する
import os, sys, numpy as np, pandas as pd
D=os.environ.get('TV_DIR','/root/.claude/uploads/7b8add96-6dec-5806-a6c7-e9425ad304f5/')
rd=lambda f: pd.read_csv(D+f,parse_dates=['time']).set_index('time').sort_index()
x=rd('fbe8b744-OANDA_XAUUSD_1D.csv'); g=rd('88023c88-CBOE_DLY_GVZ_1D.csv')
pc=x.close.shift(1); tr=((np.maximum(x.high,pc)-np.minimum(x.low,pc))/pc*100).loc['2008-07':]
fut=tr[::-1].rolling(21).mean()[::-1].shift(-1)          # 翌営業日から21日の平均
df=pd.DataFrame({'GVZ':g.close}).join(fut.rename('fut'),how='inner')
df['L']=np.log(df.GVZ); df['C']=df.L-df.L.shift(21); df['y']=np.log(df.fut)
df=df.dropna()
df['me']=df.index.to_period('M')!=pd.Series(df.index,index=df.index).shift(-1).dt.to_period('M')  # 月の最終営業日
fit=df.loc['2008-08':'2011-12']; ev=df.loc['2012-01':'2023-12']
def pred(cols):
    A=np.column_stack([np.ones(len(fit))]+[fit[c] for c in cols]); b=np.linalg.lstsq(A,fit.y,rcond=None)[0]
    return pd.Series(np.column_stack([np.ones(len(ev))]+[ev[c] for c in cols])@b,index=ev.index), b
e={}
for k,cols in {'L':['L'],'C':['C'],'L+C':['L','C']}.items():
    p,b=pred(cols); e[k]=(p-ev.y)**2; print(k,'係数',np.round(b,3))
E=pd.DataFrame(e)
# Q1
all_,me=E.L.mean(),E.L[ev.me].mean()
print(f'\nQ1 MSE 全日 {all_:.4f} / 月末 {me:.4f}（月末 {ev.me.sum()}日）→ 比 {all_/me:.3f} 判定 {all_<=me*1.10}')
# Q2
subs=[('2012','2015'),('2016','2019'),('2020','2023')]
sw=sum(E.loc[a:b,'L+C'].mean()<E.loc[a:b,'L'].mean() for a,b in subs)
r=E['L+C'].mean()/E.L.mean()
print(f'Q2 MSE L {E.L.mean():.4f} / L+C {E["L+C"].mean():.4f}（比 {r:.3f}、サブ勝ち {sw}/3）/ C単独 {E.C.mean():.4f} → 判定 {r<=0.95 and sw>=2}')
for a,b in subs: print('  ',a,b,'L',round(E.loc[a:b,'L'].mean(),4),'L+C',round(E.loc[a:b,'L+C'].mean(),4))
up=ev.C>0; print('  参考 将来RV平均: 上昇中',round(ev.fut[up].mean(),3),'/ 下落・横ばい',round(ev.fut[~up].mean(),3))
# 同じGVZ水準で比べたとき（参考）
ev2=ev.assign(band=pd.qcut(ev.GVZ,4))
print('  参考 GVZ水準別（上昇中 vs それ以外の将来RV平均）'); print(ev2.groupby(['band',up],observed=True).fut.mean().unstack().round(3))
# Q3
sys.path.insert(0,'../analysis_lvrev'); from load import t
t['ym']=pd.PeriodIndex(t.entry_time.str[:7].str.replace('.','-'),freq='M')
a=t.groupby('ym').atr_pct.median(); gm=g.close.groupby(g.index.to_period('M')).mean()
q=pd.DataFrame({'atr':a,'gvz':gm}).dropna()
b=np.polyfit(np.log(q.gvz),np.log(q.atr),1); rho=np.corrcoef(np.log(q.gvz),np.log(q.atr))[0,1]
print(f'\nQ3 月数 {len(q)} 相関 {rho:.2f} 傾き {b[0]:.2f}')
for th in (0.15,0.20): print(f'  ATR% {th} ↔ GVZ {np.exp((np.log(th)-b[1])/b[0]):.1f}')
gl=g.close.loc['2012':'2023']; print('  参考 GVZ分布 2012-23 中央値',gl.median(),'上位1/3',round(gl.quantile(2/3),1))
