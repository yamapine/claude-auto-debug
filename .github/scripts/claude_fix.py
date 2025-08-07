import os
import anthropic
import glob
import time
import sys
from typing import Optional

def extract_pine_code(response_text: str) -> str:
    """Claudeの応答からPine Scriptコードを抽出する"""
    text = response_text.strip()
    
    # ```pine または ```pinescript で囲まれたコードを抽出
    if "```pine" in text:
        start_markers = ["```pinescript", "```pine"]
        for marker in start_markers:
            if marker in text:
                code_start = text.find(marker) + len(marker)
                code_end = text.find("```", code_start)
                if code_end != -1:
                    return text[code_start:code_end].strip()
    
    # マーカーがない場合は全体を返す
    return text

def debug_pine_file(client: anthropic.Anthropic, filename: str) -> bool:
    """Pine Scriptファイルをデバッグする"""
    try:
        print(f"処理中: {filename}")
        
        # ファイル読み込み
        with open(filename, "r", encoding="utf-8") as f:
            original_code = f.read()
        
        # Claudeへの指示文（プロンプト）
        prompt = (
            f"以下はTradingView Pine Script v6のコードです。\n"
            f"バグやエラーを修正し、v6の最新仕様に準拠した正しいコードのみを返してください。\n"
            f"説明文は不要で、修正されたPine Scriptコードのみを出力してください。\n\n"
            f"```pine\n{original_code}\n```"
        )
        
        # Claude APIにリクエスト
        response = client.messages.create(
            model="claude-sonnet-4-20250514",  # 最新のClaude Sonnet 4
            max_tokens=3000,
            temperature=0,
            system="あなたは熟練したPine Script v6エンジニアです。TradingViewの最新仕様に精通しており、正確で効率的なコードを作成します。",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Claudeの返答からコード部分を抽出
        fixed_code = extract_pine_code(response.content[0].text)
        
        # バックアップファイル作成
        backup_filename = f"{filename}.backup"
        with open(backup_filename, "w", encoding="utf-8") as f:
            f.write(original_code)
        
        # 修正されたコードを書き込み
        with open(filename, "w", encoding="utf-8") as f:
            f.write(fixed_code)
        
        print(f"✓ 完了: {filename} (バックアップ: {backup_filename})")
        return True
        
    except Exception as e:
        print(f"✗ エラー: {filename} - {str(e)}")
        return False

def main():
    """メイン処理"""
    # Claude APIキー確認
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("エラー: ANTHROPIC_API_KEY環境変数が設定されていません")
        sys.exit(1)
    
    # Pine Scriptファイル検索
    pine_files = glob.glob("*.pine")
    if not pine_files:
        print("Pine Scriptファイル（*.pine）が見つかりません")
        sys.exit(1)
    
    print(f"発見されたPine Scriptファイル: {len(pine_files)}個")
    
    # Claude APIクライアント初期化
    try:
        client = anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        print(f"Claude APIクライアントの初期化エラー: {str(e)}")
        sys.exit(1)
    
    # 各ファイルを処理
    success_count = 0
    for filename in pine_files:
        if debug_pine_file(client, filename):
            success_count += 1
        
        # レート制限対策（1秒待機）
        time.sleep(1)
    
    print(f"\n処理完了: {success_count}/{len(pine_files)} ファイルが正常に処理されました")

if __name__ == "__main__":
    main()
