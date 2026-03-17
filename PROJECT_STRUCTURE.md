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

| ファイル        | 説明                                               |
| --------------- | -------------------------------------------------- |
| `README.md`     | プロジェクト全体の概要、セットアップ手順、機能説明 |
| `QUICKSTART.md` | 5分で始められるクイックガイド                      |
| `API.md`        | APIの詳細仕様、使用例、トラブルシューティング      |
| `DEPLOYMENT.md` | Azure デプロイメント手順、本番環境設定             |

### 設定ファイル

| ファイル                 | 説明                                           |
| ------------------------ | ---------------------------------------------- |
| `requirements.txt`       | Python 依存パッケージリスト                    |
| `.env.example`           | 環境変数テンプレート（コピーして .env を作成） |
| `.gitignore`             | Git除外ファイル設定                            |
| `.streamlit/config.toml` | Streamlit UI設定                               |

### スクリプト

| ファイル        | 説明                           |
| --------------- | ------------------------------ |
| `setup.py`      | 仮想環境セットアップスクリプト |
| `test_setup.py` | 環境設定の確認テスト           |
| `tests.py`      | ユニットテスト                 |

### ソースコード (src/)

| ファイル               | 説明                                                              |
| ---------------------- | ----------------------------------------------------------------- |
| `app.py`               | Streamlitアプリケーション。UI実装、ファイルアップロード、結果表示 |
| `config.py`            | 環境変数管理、書類種類定義、設定検証                              |
| `document_analyzer.py` | Azure Document Intelligence統合。PDF解析、テキスト抽出            |
| `gpt_analyzer.py`      | Azure AI Foundry統合。書類分類、情報抽出                          |

## 処理フロー

```
ユーザー操作
    ↓
┌─ L/C ファイルアップロード（左側）
├─ 複数の関連書類アップロード（右側）
└─ [🔍 Analyze & Check Discrepancies] ボタン
    ↓
[app.py] - 3ステップ処理
    ↓
    ├─ STEP 1: L/C 分析・検証
    │   ├─→ Document Intelligence 分析
    │   │   └─→ [document_analyzer.py]
    │   │       ├─ テキスト抽出
    │   │       └─ テーブル構造抽出
    │   │
    │   └─→ GPT 分析
    │       └─→ [gpt_analyzer.py: analyze_document()]
    │           ├─ 文書種別分類（1秒遅延）
    │           └─ フィールド抽出（1秒遅延）
    │               └─ L/C 検証（非 L/C は処理中断）
    │
    ├─ STEP 2: 複数ファイル順次分析
    │   ├─→ Invoice 分析
    │   ├─→ B/L 分析
    │   └─→ ...各ファイル順次処理（各 1秒遅延）
    │
    └─ STEP 3: 10項目ディスクレチェック実行
        └─→ [gpt_analyzer.py: check_discrepancies_with_lc()]
            ├─ 10項目の詳細検証（1秒遅延）
            │   ├─ 船積日、L/C有効期限、呈示期限
            │   ├─ 要求書類、建値、港湾
            │   ├─ 商品、決済方法、手数料
            │   └─ ユーザンス期日
            │
            └─ 結果表示（色分け）
                ├─ ✅ OK（緑）
                ├─ ❌ NG（赤）
                └─ ⚠️ Warning（黄）
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
AZURE_OPENAI_ENDPOINT             # Azure OpenAI Service エンドポイント
AZURE_OPENAI_API_KEY              # Azure OpenAI Service API キー
```

### オプション

```
AZURE_OPENAI_MODEL_NAME=gpt-5-mini  # 使用するGPTモデル（デフォルト）
LOG_LEVEL=INFO                      # ログレベル
```

## 書類種類とサポート

### L/C ベースディスクレパンシーチェック

**基準ドキュメント（必須）:**

- **信用状 (Letter of Credit - L/C)**
  - アップロード位置: 左側（単一ファイルのみ）
  - 役割: 比較の基準となる基本ドキュメント
  - 検証項目: L/C であることを確認

**比較対象ドキュメント（複数同時アップロード可）:**

1. **インボイス (Commercial Invoice)**
   - 抽出項目: 商品名、輸出者名、輸入者名、FOB、CFR、金額
   - ディスクレチェック項目: 商品、建値

2. **船荷証券 (Bill of Lading)**
   - 抽出項目: 商品名、輸出者名、輸入者名、船積日、呈示期限、SHIPPER、CONSIGNEE
   - ディスクレチェック項目: 船積日、呈示期限、港湾、商品

3. **航空運送状 (Air Waybill)**
   - 抽出項目: 商品名、輸出者名、輸入者名、船積日
   - ディスクレチェック項目: 船積日、商品

4. **保険証券 (Insurance Policy)**
   - 抽出項目: 保険種類、被保険者、保険金額、有効期限
   - ディスクレチェック項目: 保険カバー確認

5. **為替手形 (Bill of Exchange)**
   - 抽出項目: 輸出者名、輸入者名、手形金額、満期日
   - ディスクレチェック項目: 決済方法、ユーザンス期日

### 10項目の自動ディスクレパンシーチェック

| #   | 項目           | 検証内容                                       | 参照書類          |
| --- | -------------- | ---------------------------------------------- | ----------------- |
| 1   | 船積日         | B/L の船積日がL/C船積期限以内か                | B/L               |
| 2   | L/C有効期限    | L/C がまだ有効か                               | L/C               |
| 3   | 呈示期限       | B/L の呈示期限がL/C呈示期限以内か              | B/L               |
| 4   | 要求書類       | 必要な書類がすべてそろっているか               | L/C               |
| 5   | 建値           | Invoice と L/C の建値（FOB/CFR等）が一致するか | Invoice, L/C      |
| 6   | 港湾           | 船積地・荷揚地が一致するか                     | L/C, B/L          |
| 7   | 商品説明       | Invoice, B/L と L/C の商品説明が一致するか     | L/C, Invoice, B/L |
| 8   | 決済方法       | SWIFT コード等が正しく設定されているか         | L/C               |
| 9   | 手数料・条件   | P/O, S/A, A/A 等の条件が満たされているか       | L/C               |
| 10  | ユーザンス期日 | 為替手形の期日がL/Cの条件と一致するか          | L/C, B/E          |

## パフォーマンス

### 処理時間

**L/C + 2-3個の関連書類の場合:**

| フェーズ                         | 処理時間    | 遅延      |
| -------------------------------- | ----------- | --------- |
| Document Intelligence (L/C)      | 5-10秒      | -         |
| GPT L/C 分類                     | ~5秒        | 1秒       |
| Document Intelligence (他の書類) | 5-10秒      | -         |
| GPT 各書類抽出                   | ~5秒×N      | 1秒×N     |
| GPT ディスクレチェック           | ~10秒       | 1秒       |
| **合計**                         | **30-60秒** | **計4秒** |

### リソース要件

- **最小**: RAM 2GB、CPU 1コア
- **推奨**: RAM 4GB、CPU 2コア以上

### API 制限

- Document Intelligence: S0 tier (標準)
- Azure OpenAI: 従量課金制（gpt-5-mini）

### ボトルネック

1. **OCR 処理** (Document Intelligence): 大きなファイルで時間増加
2. **GPT API 呼び出し**: 1秒遅延×複数ファイル数分
3. **テキスト量**: 4000文字以上でトークン消費増加

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

- [x] 複数ファイルのバッチ処理 (実装完了)
- [x] L/C ベースディスクレパンシーチェック (実装完了)
- [x] 10項目自動検証 (実装完了)
- [x] 色分け表示結果 (実装完了)
- [ ] CSV/Excel エクスポート
- [ ] 抽出結果の編集機能
- [ ] 処理履歴の保存
- [ ] OCR精度の向上（パターン認識）
- [ ] キャッシング機能
- [ ] 複数言語対応
- [ ] デスクトップアプリ化
- [ ] API（REST）化

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
