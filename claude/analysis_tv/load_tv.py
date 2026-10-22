# TradingView ストラテジーの取引一覧（Smart Volume Flow OBV Strategy [3935P]・OANDA:XAUUSD）を読み込む
import os, pandas as pd
D=os.environ.get('TV_DIR','/root/.claude/uploads/7b8add96-6dec-5806-a6c7-e9425ad304f5/')
F='17eeb6b2-Smart_Volume_Flow_OBV_Strategy_3935P_OANDA_XAUUSD_2026-10-22_71c8e.csv'
d=pd.read_csv(D+F,encoding='utf-8-sig')
e=d[d.タイプ.str.contains('エントリー')].set_index('トレード番号')
x=d[d.タイプ.str.contains('決済')].set_index('トレード番号')
tr=pd.DataFrame({'side':e.タイプ.str.replace('エントリー',''),'sig_in':e.シグナル,'t_in':pd.to_datetime(e.日時),
    'p_in':pd.to_numeric(e['価格 USD'],errors='coerce'),'sig_out':x.シグナル,'t_out':pd.to_datetime(x.日時,errors='coerce'),
    'pnl_usd':x['純損益 USD'],'qty':e['サイズ (数量)'],'mfe':x['最大順行幅 USD'],'mae':x['最大逆行幅 USD'],'bars':x['期間 (バー数)']})
tr=tr[tr.t_out.notna()].copy()                    # 未決済を除く
tr['pnl']=tr.pnl_usd/tr.qty                        # 金1オンスあたり（コスト込み）
tr['y']=tr.t_out.dt.year; tr['ym']=tr.t_out.dt.to_period('M')
