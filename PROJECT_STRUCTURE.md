## プロジェクト構成

```
trade-doc-analysis/
│
├── 📄 README.md                  # プロジェクト概要
├── 📄 QUICKSTART.md              # クイックスタートガイド
├── 📄 API.md                     # API仕様書
├── 📄 DEPLOYMENT.md              # デプロイメントガイド
│
├── 📋 requirements.txt           # Python依存パッケージ
├── 📋 .env.example              # 環境変数テンプレート
├── 📋 .gitignore                # Git除外設定
│
├── 🔧 setup.py                  # セットアップスクリプト
├── 🧪 test_setup.py             # セットアップテストスクリプト
├── 🧪 tests.py                  # ユニットテスト
│
├── 📁 src/                      # メインコードディレクトリ
│   ├── 🐍 app.py               # Streamlitメインアプリ
│   ├── ⚙️  config.py            # 設定・定数管理
│   ├── 📄 document_analyzer.py  # Document Intelligence ラッパー
│   └── 🤖 gpt_analyzer.py       # Azure AI Foundry GPT統合
│
├── 📁 .streamlit/               # Streamlit設定
│   └── config.toml             # Streamlit設定ファイル
│
├── 📁 .git/                     # Gitリポジトリ
│
└── 📄 LICENSE                   # ライセンス

```

## ファイル説明

### メインドキュメント

| ファイル | 説明 |
|---------|------|
| `README.md` | プロジェクト全体の概要、セットアップ手順、機能説明 |
| `QUICKSTART.md` | 5分で始められるクイックガイド |
| `API.md` | APIの詳細仕様、使用例、トラブルシューティング |
| `DEPLOYMENT.md` | Azure デプロイメント手順、本番環境設定 |

### 設定ファイル

| ファイル | 説明 |
|---------|------|
| `requirements.txt` | Python 依存パッケージリスト |
| `.env.example` | 環境変数テンプレート（コピーして .env を作成） |
| `.gitignore` | Git除外ファイル設定 |
| `.streamlit/config.toml` | Streamlit UI設定 |

### スクリプト

| ファイル | 説明 |
|---------|------|
| `setup.py` | 仮想環境セットアップスクリプト |
| `test_setup.py` | 環境設定の確認テスト |
| `tests.py` | ユニットテスト |

### ソースコード (src/)

| ファイル | 説明 |
|---------|------|
| `app.py` | Streamlitアプリケーション。UI実装、ファイルアップロード、結果表示 |
| `config.py` | 環境変数管理、書類種類定義、設定検証 |
| `document_analyzer.py` | Azure Document Intelligence統合。PDF解析、テキスト抽出 |
| `gpt_analyzer.py` | Azure AI Foundry統合。書類分類、情報抽出 |

## 処理フロー

```
ユーザー操作
    ↓
PDFファイルアップロード
    ↓
[app.py]
    ↓
    ├─→ Document Intelligence 分析
    │   └─→ [document_analyzer.py]
    │       ├─ テキスト抽出
    │       └─ テーブル構造抽出
    │
    ├─→ GPT分析
    │   └─→ [gpt_analyzer.py]
    │       ├─ 書類種類分類
    │       └─ 詳細情報抽出
    │
    └─→ 結果表示
        ├─ 書類種類
        ├─ 抽出フィールド
        └─ 追加情報
```

## 依存関係図

```
app.py (Streamlit UI)
  ├─ config.py (設定)
  ├─ document_analyzer.py
  │   └─ azure.ai.documentintelligence
  └─ gpt_analyzer.py
      └─ requests (HTTP)
          └─ Azure OpenAI API
```

## 環境変数

### 必須

```
DOCUMENT_INTELLIGENCE_ENDPOINT    # Document Intelligence エンドポイント
DOCUMENT_INTELLIGENCE_KEY          # Document Intelligence API キー
AZURE_AI_FOUNDRY_ENDPOINT         # AI Foundry エンドポイント
AZURE_AI_FOUNDRY_API_KEY          # AI Foundry API キー
```

### オプション

```
AZURE_AI_FOUNDRY_MODEL=gpt-4-mini  # 使用するGPTモデル（デフォルト）
LOG_LEVEL=INFO                     # ログレベル
```

## 書類種類とサポート

### 対応書類

1. **インボイス (Commercial Invoice)**
   - 抽出項目: 商品名、輸出者名、輸入者名、FOB、CFR

2. **船荷証券 (Bill of Lading)**
   - 抽出項目: 商品名、輸出者名、輸入者名、船積日、呈示期限、SHIPPER、CONSIGNEE、NOTIFY、裏書

3. **航空運送状 (Air Waybill)**
   - 抽出項目: 商品名、輸出者名、輸入者名、船積日

4. **保険証券 (Insurance Policy)**
   - 抽出項目: 保険種類、被保険者、保険金額、有効期限

5. **為替手形 (Bill of Exchange)**
   - 抽出項目: 輸出者名、輸入者名、手形金額、満期日

6. **信用状 (Letter of Credit)**
   - 抽出項目: L/C番号、開設依頼人、受益者、L/C期限、船積期限、呈示期間、L/C開設金額、現在残、商品、原産地、船積地、荷揚地、要求書類

## パフォーマンス

### 処理時間

- Document Intelligence: 2-5秒 (ファイルサイズによる)
- GPT分析: 5-15秒 (テキスト量による)
- 合計: 10-30秒程度

### リソース要件

- **最小**: RAM 2GB、CPU 1コア
- **推奨**: RAM 4GB、CPU 2コア

### API 制限

- Document Intelligence: S0 tier (標準)
- Azure AI Foundry: 従量課金制

## セキュリティ

- 環境変数で認証情報を管理
- .env ファイルは .gitignore に含まれている
- HTTPS で Azure API と通信
- API キーをログに出力しない

## 拡張性

### カスタマイズ可能な部分

1. **書類種類の追加**
   - `config.py` の `DOCUMENT_TYPES` を更新

2. **抽出フィールドの変更**
   - `config.py` の対応する書類種類のフィールドリストを編集

3. **UI のカスタマイズ**
   - `app.py` の Streamlit コンポーネントを変更

4. **プロンプトの改善**
   - `gpt_analyzer.py` の `_classify_document_type()` と `_extract_detailed_info()` を修正

## ログ出力

- Streamlit ターミナルに INFO レベルのログを出力
- 各処理段階でステータスメッセージを表示

## 今後の機能予定

- [ ] 複数ファイルのバッチ処理
- [ ] CSV/Excel エクスポート
- [ ] 抽出結果の編集機能
- [ ] 処理履歴の保存
- [ ] OCR精度の向上
- [ ] キャッシング機能
- [ ] 複数言語対応

## 開発者向け情報

### テストの実行

```bash
# セットアップ確認
python test_setup.py

# ユニットテスト
python -m unittest tests.py
```

### ローカル開発

```bash
# Streamlit開発モード
streamlit run src/app.py --logger.level=debug

# コードフォーマット
# (black などのフォーマッターを使用)
```

### デバッグ

`config.py` の `LOG_LEVEL` を "DEBUG" に変更すると詳細ログが出力されます。
