import os
import anthropic
import glob

# Claude APIキー（GitHub Secretsで登録したもの）
API_KEY = os.environ["ANTHROPIC_API_KEY"]

# リポジトリ直下の *.pine ファイルすべて取得
pine_files = glob.glob("*.pine")

# Claude APIクライアントを初期化
client = anthropic.Anthropic(api_key=API_KEY)

for fname in pine_files:
    with open(fname, "r") as f:
        code = f.read()

    # Claudeへの指示文（プロンプト）
    prompt = (
        f"以下はTradingView Pine Scriptコードです。バグやエラーを修正した正しいコードのみ返してください。\n\n"
        f"```pine\n{code}\n```"
    )

    # Claude APIにリクエスト
    response = client.messages.create(
        model="claude-sonnet-4-20250514",  # 最新のモデル名
        max_tokens=2048,
        temperature=0,
        system="あなたは優秀なPine Scriptエンジニアです。",
        messages=[{"role": "user", "content": prompt}]
    )
    # Claudeの返答からコード部分を抽出
    fixed_code = response.content[0].text.strip()
    if fixed_code.startswith("```pine"):
        fixed_code = fixed_code.split("```pine")[1]
    fixed_code = fixed_code.replace("```", "").strip()
    with open(fname, "w") as f:
        f.write(fixed_code)
