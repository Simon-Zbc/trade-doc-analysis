# Quick Start Guide

## 5分で始める

### 1. 環境構築

```bash
# プロジェクトディレクトリに移動
cd trade-doc-analysis

# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化 (Windows)
venv\Scripts\activate

# 仮想環境を有効化 (Mac/Linux)
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 2. Azure クレデンシャルの設定

```bash
# .env ファイルを作成
copy .env.example .env
```

`.env` ファイルを編集して、以下の値を入力してください：

```
DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-region.api.cognitive.microsoft.com/
DOCUMENT_INTELLIGENCE_KEY=your-api-key

AZURE_AI_FOUNDRY_ENDPOINT=https://your-region.openai.azure.com/
AZURE_AI_FOUNDRY_API_KEY=your-api-key
AZURE_AI_FOUNDRY_MODEL=gpt-4-mini
```

### 3. セットアップの確認

```bash
python test_setup.py
```

### 4. アプリを起動

```bash
streamlit run src/app.py
```

アプリがブラウザで開きます（http://localhost:8501）

## 使用方法

1. **ファイルをアップロード**
   - PDFファイルをアップロードエリアにドラッグ&ドロップ、または選択

2. **分析ボタンをクリック**
   - "🔍 Analyze" ボタンをクリック
   - 処理が進行します（10-30秒程度）

3. **結果を確認**
   - 書類の種類が表示されます
   - 抽出された情報がリストアップされます

4. **リセット**
   - "🗑️ Clear" ボタンで結果をクリア

## Azure認証情報の取得方法

### Document Intelligence

1. [Azure Portal](https://portal.azure.com) にログイン
2. "Document Intelligence" リソースを検索または作成
3. "Keys and Endpoint" セクションをクリック
4. **Endpoint** をコピー → `DOCUMENT_INTELLIGENCE_ENDPOINT`
5. **Key 1** をコピー → `DOCUMENT_INTELLIGENCE_KEY`

### Azure AI Foundry

#### 方法1: Azure AI Foundry 経由（推奨）

1. [Azure AI Foundry](https://ai.azure.com) にアクセス
2. プロジェクトを作成または選択
3. "Deployments" → "Deploy model" → "gpt-4-mini" を選択
4. "Manage Deployments" → デプロイ名を確認
5. "Credentials & Keys" からエンドポイントとキーをコピー

#### 方法2: Azure OpenAI Service 経由

1. [Azure Portal](https://portal.azure.com) で "OpenAI" を検索
2. OpenAI リソースを作成
3. "Keys and Endpoint" からエンドポイントとキーをコピー
4. "Model deployments" でモデルをデプロイ

## トラブルシューティング

### "Missing required environment variables" エラー

→ `.env` ファイルが存在し、すべての値が正しく設定されているか確認してください

### "Import error: azure.ai.documentintelligence"

→ 次のコマンドでパッケージをインストール：
```bash
pip install azure-ai-documentintelligence --upgrade
```

### ファイルアップロード後に「Error」が表示される

→ 以下を確認してください：
- Azure認証情報が正しいか
- ネットワーク接続があるか
- Azure リソースが有効か

### 処理が完了しない

→ 少し待ってください（10-30秒程度必要な場合があります）

## サポートされている書類種類

| 種類 | 英語名 |
|------|--------|
| インボイス | Commercial Invoice |
| 船荷証券 | Bill of Lading (B/L) |
| 航空運送状 | Air Waybill (AWB) |
| 保険証券 | Insurance Policy |
| 為替手形 | Bill of Exchange |
| 信用状 | Letter of Credit (L/C) |

## 次のステップ

- 複数の書類を処理してみる
- 結果をCSVにエクスポート（機能予定）
- カスタム抽出フィールドの設定（機能予定）

## さらに詳しく

- [README.md](README.md) - 詳細なドキュメント
- [API.md](API.md) - API仕様書
- [DEPLOYMENT.md](DEPLOYMENT.md) - デプロイメントガイド

## お問い合わせ

問題が発生した場合は、以下をお試しください：

1. `test_setup.py` を実行して環境を確認
2. Azure Portal でリソースが正常に動作しているか確認
3. ログをチェック（Streamlit UI に表示されます）
