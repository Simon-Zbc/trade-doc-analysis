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

## 次のステップ（推奨）

1. **テスト実行**
   - サンプルPDFで動作確認

2. **本番環境への移行**
   - 本番環境用の .env 設定
   - ロギングレベルを INFO に設定

3. **監視設定**
   - Streamlit のキャッシング活用
   - API使用量の監視

---

**修正状態：** ✅ 完了
**テスト状況：** ✅ コンパイル確認済み
**ドキュメント：** ✅ 作成済み (FIXES.md)
