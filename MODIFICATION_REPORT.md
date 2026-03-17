# 修正完了レポート

## 修正日時

2026年3月13日

## 修正内容サマリー

### ✅ 実施した修正

#### 1. ログ出力機能の追加

**ファイル:** `src/document_analyzer.py`

```python
# document_analyzer.py の analyze_document() メソッド
logger.info(f"✅ Extracted pages: {len(result.pages) if result.pages else 0}")
logger.info(f"✅ Extracted tables: {len(tables_data)}")
logger.info(f"✅ Text length: {len(extracted_text)} characters")
logger.info(f"📋 Document Analysis Result: {result_dict}")
```

**効果：** ターミナルに以下が表示されます

```
✅ Extracted pages: 5
✅ Extracted tables: 3
✅ Text length: 12450 characters
📋 Document Analysis Result: {...}
```

---

#### 2. GPT API エラーの修正

**ファイル:** `src/gpt_analyzer.py`

##### 問題：400 Bad Request

```
ERROR:gpt_analyzer:Error calling GPT API: 400 Client Error: Bad Request for url:
https://test-smbc-foundry.openai.azure.com/openai/v1/chat/completions
```

##### 修正内容：

###### 2-1. 認証ヘッダーの修正

```python
# ❌ 修正前
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {self.api_key}"
}

# ✅ 修正後
headers = {
    "Content-Type": "application/json",
    "api-key": self.api_key  # Azure OpenAI uses api-key header
}
```

**理由：** Azure OpenAI API は `api-key` ヘッダーを使用（`Authorization: Bearer` ではない）

###### 2-2. エンドポイント形式の修正

```python
# ❌ 修正前
f"{self.endpoint.rstrip('/')}/chat/completions"
# 結果: https://test-smbc-foundry.openai.azure.com/chat/completions

# ✅ 修正後
f"{api_url}/openai/deployments/{self.model}/chat/completions?api-version=2024-02-15-preview"
# 結果: https://test-smbc-foundry.openai.azure.com/openai/deployments/gpt-4-mini/chat/completions?api-version=2024-02-15-preview
```

**理由：** Azure OpenAI は deployment-based URL を要求

###### 2-3. ペイロード形式の修正

```python
# ❌ 修正前
payload = {
    "model": self.model,  # ← Azure では不要
    "messages": [...],
    "temperature": 0.7,
    "max_tokens": 2000
}

# ✅ 修正後
payload = {
    "messages": [...],
    "temperature": 0.7,
    "max_tokens": 2000
}
```

**理由：** Azure OpenAI ではモデルがURLに含まれているため、ペイロードに不要

###### 2-4. システムプロンプトの改善

```python
# より明確なJSON出力を指示
"You are a helpful assistant that analyzes trade documents. Always respond in valid JSON format only, without any markdown formatting or code blocks."
```

###### 2-5. レスポンス解析の強化

````python
# Markdownフォーマットに対応
response_text = response.strip()
if response_text.startswith('```json'):
    response_text = response_text[7:]
if response_text.startswith('```'):
    response_text = response_text[3:]
if response_text.endswith('```'):
    response_text = response_text[:-3]

result = json.loads(response_text)
````

---

#### 3. 詳細なログ出力の追加

**分類フェーズ**

```
🔍 Classifying document type...
✅ Document classified as: インボイス（商業送り状） (Commercial Invoice)
   Confidence: 95%
```

**詳細情報抽出フェーズ**

```
📝 Extracting detailed information for invoice...
✅ Information extraction completed
   Fields extracted: 5 items
```

**API呼び出しログ**

```
💬 Calling GPT API with model: gpt-4-mini
Endpoint: https://test-smbc-foundry.openai.azure.com
✅ GPT API Response received
```

**エラーハンドリング**

```
❌ Error calling GPT API: 400 Client Error: Bad Request...
❌ Error classifying document: Unknown document class: unknown
❌ Error in GPT analysis: ...
```

---

### 📝 修正ファイル一覧

| ファイル                   | 修正内容                                                    |
| -------------------------- | ----------------------------------------------------------- |
| `src/document_analyzer.py` | ログ出力機能追加（✅ Extracted pages, tables, text length） |
| `src/gpt_analyzer.py`      | APIエラー修正、ログ追加、エラーハンドリング強化             |
| `FIXES.md`                 | 修正内容の詳細ドキュメント新規作成                          |

---

## 確認・テスト方法

### 1. コンパイルテスト

```bash
cd trade-doc-analysis
python -m py_compile src/document_analyzer.py src/gpt_analyzer.py
# ✅ Compilation successful が表示されれば成功
```

### 2. アプリ起動

```bash
# 仮想環境を有効化
venv\Scripts\activate

# インストール
pip install -r requirements.txt

# .env ファイルを設定
copy .env.example .env
# Azure認証情報を入力

# アプリ起動
streamlit run src/app.py
```

### 3. ログの確認

ターミナルに以下のように表示されます：

```
Starting document analysis for invoice.pdf
✅ Extracted pages: 3
✅ Extracted tables: 2
✅ Text length: 8500 characters
📋 Document Analysis Result: {...}
🔍 Classifying document type...
💬 Calling GPT API with model: gpt-4-mini
✅ Document classified as: インボイス（商業送り状） (Commercial Invoice)
   Confidence: 95%
📝 Extracting detailed information for invoice...
💬 Calling GPT API with model: gpt-4-mini
✅ Information extraction completed
   Fields extracted: 5 items
```

---

## 環境設定の確認

### .env ファイルのフォーマット

```ini
# Azure Document Intelligence
DOCUMENT_INTELLIGENCE_ENDPOINT=https://{region}.api.cognitive.microsoft.com/
DOCUMENT_INTELLIGENCE_KEY={your-key}

# Azure OpenAI (修正済み)
AZURE_AI_FOUNDRY_ENDPOINT=https://{resource-name}.openai.azure.com
AZURE_AI_FOUNDRY_API_KEY={your-api-key}
AZURE_AI_FOUNDRY_MODEL=gpt-4-mini
```

**重要:** エンドポイントは `.openai.azure.com` で終わる（末尾に余分なパスはなし）

---

## トラブルシューティング

### 問題: まだ 400 Bad Request が発生する

**確認項目：**

1. ✅ エンドポイント形式
   - 正: `https://resource-name.openai.azure.com`
   - 誤: `https://resource-name.openai.azure.com/openai/v1` (末尾に /v1 がある)

2. ✅ APIキーが有効か
   - Azure Portal で "Keys and Endpoint" を確認

3. ✅ モデルデプロイ名が正確か
   - `AZURE_AI_FOUNDRY_MODEL=gpt-4-mini` が実際のデプロイ名と一致しているか確認

4. ✅ ログで詳細を確認
   - `logger.debug()` メッセージで API URL を確認

---

## パフォーマンス

修正による改善：

- ⚡ エラーハンドリングの堅牢性向上
- 📊 詳細なログにより問題の特定が容易化
- 🎯 Markdownフォーマットのレスポンスに対応
- 🔐 Azure OpenAI の最新APIに準拠

---

## 追加修正（2026年3月13日）

### 1. OpenAI SDK の更新と互換性改善

**ファイル:** `src/gpt_analyzer.py`

#### 修正内容：

##### 1-1. インポート形式の変更（Microsoft公式ドキュメント準拠）

```python
# ❌ 修正前
from openai import AzureOpenAI

self.client = AzureOpenAI(
    api_key=self.api_key,
    api_version="2025-04-01-preview",
    azure_endpoint=self.endpoint
)

# ✅ 修正後
from openai import OpenAI

base_url = f"{self.endpoint.rstrip('/')}/openai/v1/"
self.client = OpenAI(
    api_key=self.api_key,
    base_url=base_url
)
```

**理由：** Microsoftの公式ドキュメント（[Azure OpenAI でサポートされているプログラミング言語](https://learn.microsoft.com/ja-jp/azure/foundry/openai/supported-languages?pivots=programming-language-python)）で推奨されている形式

##### 1-2. API パラメータの更新

```python
# ❌ 修正前
response = self.client.chat.completions.create(
    model=self.model,
    messages=[...],
    temperature=0.7,
    max_tokens=2000
)

# ✅ 修正後
response = self.client.chat.completions.create(
    model=self.model,
    messages=[...],
    max_completion_tokens=2000
)
```

**変更理由：**

- `max_tokens` → `max_completion_tokens`：新しいAPIバージョンで標準化
- `temperature` 削除：このモデルはデフォルト値（1）のみをサポート

### 2. 依存関係の最適化

**ファイル:** `requirements.txt`

```
# ✅ 更新されたバージョン
streamlit==1.40.2
openai==1.42.0
azure-ai-documentintelligence==1.0.2
azure-identity==1.14.0
```

### 3. ドキュメントの更新

**更新されたファイル：**

- ✅ `README.md` - 抽出フィールドを最新の設定に更新
- ✅ `API.md` - DOCUMENT_TYPES の完全な定義を追加
- ✅ このレポート - 最新の修正情報を追記

### 修正の効果

| 項目                   | 修正前                   | 修正後                |
| ---------------------- | ------------------------ | --------------------- |
| **インポート方式**     | AzureOpenAI（Azure専用） | OpenAI（汎用）        |
| **API互換性**          | 一部パラメータ非サポート | 最新APIに完全対応     |
| **エンドポイント管理** | api_version パラメータ   | base_url パラメータ   |
| **トークン制限**       | max_tokens               | max_completion_tokens |
| **Temperature**        | 0.7（カスタム）          | デフォルト値のみ      |

### テスト状況

✅ **検証完了：**

- GPTAnalyzer クラスの初期化成功
- OpenAI SDK との統合確認
- API パラメータの互換性確認

---

## 大規模アーキテクチャ変更 (2026年3月16-17日)

### 📋 変更概要

**従来:** 2つのファイルを並べて比較（左右対称の分析）
**新規:** Letter of Credit (L/C) を基準として、複数の関連書類 (Invoice, B/L など) を検証する 10 項目のディスクレパンシーチェック

### 🔧 Backend 修正 (src/gpt_analyzer.py)

#### 新メソッド: `check_discrepancies_with_lc()`

```python
def check_discrepancies_with_lc(
    self,
    lc_analysis: Dict[str, Any],
    other_files_analyses: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    L/C を基準に 10 項目の詳細ディスクレパンシーチェックを実施
    """
```

**実装された 10 項目チェック:**

1. 船積日（Shipment Date Verification）
2. L/C 有効期限（L/C Expiration Check）
3. 呈示期限（Presentation Period Verification）
4. 要求書類の不備（Required Documents Check）
5. 建値（Price Terms Verification）
6. 港湾（Ports Verification）
7. 商品説明（Goods Description Check）
8. 対外決済方法（Settlement Method Check）
9. 手数料・条件（Fees and Conditions Check）
10. ユーザンス期日（Usance Period Verification）

#### API 呼び出しの最適化

```python
import time

# 各 GPT 呼び出し前に 1 秒遅延を実装（計 4 箇所）
- L/C 分類前：time.sleep(1)
- L/C 抽出前：time.sleep(1)
- 関連書類分析前：time.sleep(1)
- ディスクレチェック前：time.sleep(1)
```

**目的:** API rate limiting の遵守と安定性向上

### 🎨 Frontend 修正 (src/app.py)

#### セッションステート完全書き替え

```python
# 変更前
st.session_state.uploaded_file_1/2
st.session_state.analysis_result_1/2
st.session_state.comparison_result

# 変更後
st.session_state.uploaded_lc              # L/C ファイル（単一）
st.session_state.uploaded_other_files     # 複数ファイル
st.session_state.lc_analysis_result       # L/C 分析結果
st.session_state.other_files_analysis_results  # 各ファイルの分析結果
st.session_state.discrepancy_check_result # 10 項目チェック結果
```

#### UI レイアウト変更

**前:**

```
┌─ 左側: ファイル1
├─ 右側: ファイル2
└─ 比較結果
```

**後:**

```
┌─ 左側: L/C（単一、必須）
├─ 右側: 複数ファイル（複数、複数アップロード可）
└─ L/C 検証 → 複数ファイル分析 → 10 項目チェック
```

#### 処理フロー書き直し（analyze_documents()）

```python
# 3 ステップフロー
1. L/C ファイル分析・検証
   └─ 非 L/C ファイルの場合、処理中断

2. 複数ファイル順次分析
   ├─ Invoice-分析
   ├─ B/L-分析
   └─ ...各ファイル順次処理

3. 10 項目ディスクレチェック実行
   └─ 結果表示（色分け: ✅ OK / ❌ NG / ⚠️ Warning）
```

### 📊 修正ファイル一覧

| ファイル              | 修正内容                                     |
| --------------------- | -------------------------------------------- |
| `src/gpt_analyzer.py` | `check_discrepancies_with_lc()` メソッド追加 |
| `src/app.py`          | 完全書き直し（L/C + 複数ファイルモデル対応） |
| `src/config.py`       | 変更なし（既存）                             |
| `UPDATE_NOTES.md`     | L/C システム説明を追加                       |

### 🎯 主な改善点

| 項目                 | 従来（2ファイル比較） | 新規（L/C ディスクレチェック） |
| -------------------- | --------------------- | ------------------------------ |
| **基準ドキュメント** | 同等レベル            | L/C 優先                       |
| **ファイル数**       | 2 つ限定              | 複数（3～5推奨）               |
| **チェック項目**     | フィールド比較        | 10 項目詳細検証                |
| **表示形式**         | 左右対称              | L/C + タブ表示                 |
| **エラー処理**       | 非区別                | L/C 検証失敗で処理中断         |
| **色分け表示**       | 相違あり/なし         | ✅ OK / ❌ NG / ⚠️ Warning     |

### ✅ テスト確認

```bash
# コンパイルテスト
python -m py_compile src/gpt_analyzer.py src/app.py

# インポートテスト
python -c "from src.gpt_analyzer import GPTAnalyzer; from src.app import analyze_documents"

# 実行テスト
streamlit run src/app.py
```

### 📝 ドキュメント更新

- ✅ `UPDATE_NOTES.md` - L/C システム完全説明
- ✅ `README.md` - アーキテクチャ説明更新
- ✅ `API.md` - `check_discrepancies_with_lc()` ドキュメント追加

---

**修正状態：** ✅ 完了
**テスト状況：** ✅ システム全体確認済み
**ドキュメント：** ✅ 最新化完了
**テストチェックリスト：** ✅ 全項目実施
