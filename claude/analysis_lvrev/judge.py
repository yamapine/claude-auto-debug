import sys; sys.path.insert(0,'.')
from load import *
Y=(2024,2025,2026)
F=sorted(s['filter'].unique())
def c1(r,b): return all(r[f'y{y}_net']>=b[f'y{y}_net'] and r[f'y{y}_pf']>=b[f'y{y}_pf'] for y in (2024,2025))
def c2(r,b): return r.y2026_net>=0.9*b.y2026_net and r.y2026_pf>=b.y2026_pf-0.05
def c3(r): return all(r[f'y{y}_n']>=30 for y in Y)
base=s.set_index(KEY+['filter'])
# ---- 判定A
print('=== 判定A（基準: Z3/doten_lock/SL5/both）')
rows=[]
for v in ['V1','V2','V3','V4']:
    b=base.loc[(v,3.0,'doten_lock',5.0,'both','none')]
    rows.append(dict(MA=v,filter='none',**{f'{y}_{k}':b[f'y{y}_{k}'] for y in Y for k in ('n','net','pf')}))
    for f in [x for x in F if x!='none']:
        r=base.loc[(v,3.0,'doten_lock',5.0,'both',f)]
        rows.append(dict(MA=v,filter=f,**{f'{y}_{k}':r[f'y{y}_{k}'] for y in Y for k in ('n','net','pf')},
            rev_n=r.rev_n,revsl_n=r.revsl_n,skip_n=r.skip_n,A1=c1(r,b),A2=c2(r,b),A3=c3(r)))
A=pd.DataFrame(rows)
# ④ 隣接閾値: 同系(lvrev同SL / atr_pct)で隣の閾値も①
def fam(f):
    if f.startswith('lvrev'): return 'lv_'+f.split('_')[1], float(f[5:9])
    if f.startswith('atr'): return 'atr', float(f.split('>=')[1])
    return None,None
A['fam'],A['th']=zip(*A['filter'].map(fam))
def a4(row):
    if row['filter']=='none': return None
    sib=A[(A.MA==row.MA)&(A.fam==row.fam)&(A['filter']!=row['filter'])]
    sib=sib[(sib.th-row.th).abs().round(3)==0.02]
    return bool(sib.A1.all()) if len(sib) else None
A['A4']=A.apply(a4,axis=1)
A['A_pass']=A.A1&A.A2&A.A3&(A.A4==True)
pd.set_option('display.width',250)
print(A.drop(columns=['fam','th']).round(3).to_string(index=False))
A.to_csv('judgeA.csv',index=False)
# ---- 判定B
print('\n=== 判定B（全条件 / F0で各年30件以上）')
out=[]
for f in [x for x in F if x!='none']:
    rec=dict(filter=f)
    ok3=0
    for v in ['V1','V2','V3','V4']:
        sub=s[s.variant==v]
        b0=sub[sub['filter']=='none'].set_index(KEY)
        bf=sub[sub['filter']==f].set_index(KEY)
        elig=b0[(b0.y2024_n>=30)&(b0.y2025_n>=30)&(b0.y2026_n>=30)].index
        p1=sum(c1(bf.loc[i],b0.loc[i]) for i in elig)/len(elig)
        p2=sum(c2(bf.loc[i],b0.loc[i]) for i in elig)/len(elig)
        rec[f'{v}_N']=len(elig); rec[f'{v}_p1']=round(p1*100,1); rec[f'{v}_p2']=round(p2*100,1)
        ok3+= (p1>=0.6 and p2>=0.7)
    rec['MA合格数']=ok3; rec['B_pass']=ok3>=3
    out.append(rec)
B=pd.DataFrame(out); print(B.to_string(index=False)); B.to_csv('judgeB.csv',index=False)
