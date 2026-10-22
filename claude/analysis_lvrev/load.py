import pandas as pd
import os
# CSV置き場（環境変数 SVF_DIR で変更可）
U=os.environ.get('SVF_DIR','/root/.claude/uploads/7b8add96-6dec-5806-a6c7-e9425ad304f5/')
s=pd.read_csv(U+'399f8db3-SVF_Sweep_XAUUSD_M15.csv')
m=pd.read_csv(U+'51ee01a6-SVF_Monthly_XAUUSD_M15.csv')
t=pd.read_csv(U+'123f443f-SVF_Trades_XAUUSD_M15.csv',encoding='cp932')
KEY=['variant','zTh','band','sl_atr','dir']
