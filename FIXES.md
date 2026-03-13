# Fix Summary - Logging and GPT API Error Resolution

## 修正内容

### 1. ✅ ログ出力機能の追加

#### document_analyzer.py

以下の出力をターミナルにログとして出力するように修正しました：

```
✅ Extracted pages: {page_count}
✅ Extracted tables: {table_count}
✅ Text length: {text_length} characters
📋 Document Analysis Result: {result_dict}
```

**修正内容：**

- `analyze_document()` メソッドで詳細なログ出力を追加
- 抽出されたページ数、テーブル数、テキスト長を表示
- 最終結果をJSON形式でログ出力

### 2. ✅ GPT API エラーの修正

#### gpt_analyzer.py

**問題：**

```
ERROR: 400 Client Error: Bad Request for url: https://test-smbc-foundry.openai.azure.com/openai/v1/chat/completions
```

**原因：**

- Azure OpenAI API の認証ヘッダーが不正
- エンドポイント形式が不正
- ペイロード形式が不正

**修正内容：**

1. **認証ヘッダーの修正**

   ```python
   # 修正前
   headers = {
       "Authorization": f"Bearer {self.api_key}"
   }

   # 修正後
   headers = {
       "api-key": self.api_key  # Azure OpenAI uses api-key header
   }
   ```

2. **エンドポイント形式の修正**

   ```python
   # Azure OpenAI の正しいエンドポイント形式
   https://{resource-name}.openai.azure.com/openai/deployments/{deployment-name}/chat/completions?api-version=2024-02-15-preview

   # 修正内容：
   - エンドポイントに `/openai/deployments/{model}/` を追加
   - APIバージョン `2024-02-15-preview` を指定
   ```

3. **ペイロード形式の修正**

   ```python
   # 修正前
   payload = {
       "model": self.model,  # ← 不要（Azure OpenAIではURLに含める）
       "messages": [...],
       ...
   }

   # 修正後
   payload = {
       "messages": [...],
       "temperature": 0.7,
       "max_tokens": 2000
   }
   ```

4. **システムプロンプトの改善**

   ```python
   # 修正前
   "You are a helpful assistant that analyzes trade documents. Always respond in JSON format."

   # 修正後
   "You are a helpful assistant that analyzes trade documents. Always respond in valid JSON format only, without any markdown formatting or code blocks."
   ```

5. **レスポンス解析の強化**
   - Markdownフォーマッティング（`json ... `）をサポート
   - JSON解析エラー時の詳細ログを追加

### 3. ✅ 詳細なログ出力の追加

#### 分類フェーズ

```
🔍 Classifying document type...
✅ Document classified as: インボイス（商業送り状） (Commercial Invoice)
   Confidence: 95%
```

#### 詳細情報抽出フェーズ

```
📝 Extracting detailed information for invoice...
✅ Information extraction completed
   Fields extracted: 5 items
```

#### API呼び出しログ

```
💬 Calling GPT API with model: gpt-4-mini
✅ GPT API Response received
```

#### エラー時のログ

```
❌ Error calling GPT API: 400 Client Error: Bad Request...
❌ Error classifying document: ...
❌ Error in GPT analysis: ...
```

## 設定変更点

### .env ファイルの更新

Azure OpenAI を使用する場合、以下の形式で設定してください：

```
AZURE_AI_FOUNDRY_ENDPOINT=https://{resource-name}.openai.azure.com
AZURE_AI_FOUNDRY_API_KEY={your-api-key}
AZURE_AI_FOUNDRY_MODEL=gpt-4-mini
```

**重要：** エンドポイントは `.openai.azure.com` で終わる（末尾に `/openai/deployments` は不要）

## テスト方法

### ターミナルでログを確認

```bash
# 仮想環境を有効化
venv\Scripts\activate

# アプリを起動（Streamlitはターミナルにログを出力）
streamlit run src/app.py
```

### ログレベルの設定

`.env` ファイルでログレベルを設定：

```
LOG_LEVEL=DEBUG  # より詳細なログを出力
```

## トラブルシューティング

### 仍然として 400 Bad Request が発生する場合

1. **エンドポイントを確認**
   - Azure Portal で "Document Intelligence" → "Deployments" → "Endpoints" を確認
   - 形式：`https://{resource-name}.openai.azure.com`

2. **APIキーを確認**
   - Azure Portal で "Keys and Endpoint" セクションを確認
   - キーが有効期限内か確認

3. **モデルデプロイメント名を確認**
   - Azure Portal で実際のデプロイ名を確認
   - `AZURE_AI_FOUNDRY_MODEL` に設定されているが正しいか確認

4. **ログで詳細を確認**
   - ターミナルに出力されるエラーメッセージを確認
   - `logger.debug()` のメッセージで API URL とペイロードを確認

## パフォーマンス改善

修正により以下が改善されました：

- ✅ エラーハンドリングが堅牢に
- ✅ 詳細なログにより問題の特定が容易
- ✅ Markdownフォーマットのレスポンスに対応
- ✅ Azure OpenAI の正しいAPI形式に準拠

## 今後の改善予定

- [ ] キャッシング機構の実装
- [ ] リトライロジックの追加
- [ ] 複数エンドポイント対応
- [ ] タイムアウト設定の最適化
