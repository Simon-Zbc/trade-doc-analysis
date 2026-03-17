# 機能更新メモ (2026年3月17日)

## 📋 更新内容 - Letter of Credit ディスクレチェック機能の全面実装

### ✨ 新機能

### ✨ 新機能

#### 1. Letter of Credit (L/C) 基準のディスクレチェック

- 信用状（Letter of Credit）を基準ドキュメントとして使用
- 関連する複数の貿易書類（Invoice、B/L、AWB など）と自動比較
- **10項目の詳細チェック**を実施

#### 2. 複数ファイル対応

- **左側**: Letter of Credit のみ（単一ファイル）
- **右側**: 複数の関連書類（Invoice、B/L、AWB など複数同時アップロード）

#### 3. 10項目の自動ディスクレチェック

1. 船積日（B/L との比較）
2. L/C 有効期限
3. 呈示期限（B/L との比較）
4. 要求書類の不備（通数チェック）
5. 建値（FOB/CFR vs FREIGHT PREPAID/COLLECT）
6. 船積地・荷揚地
7. 商品（B/L、Invoice との比較）
8. 対外決済方法（SWIFT ADDRESS）
9. 手数料負担区分、P/O、S/A、A/A 要否
10. ユーザンス期日

#### 4. 色分けされた結果表示

- **✅ OK** （緑）：相違なし
- **❌ NG** （赤）：相違あり
- **⚠️ Warning** （黄）：注意が必要

---

## 🔧 実装内容

### Backend 修正 (src/gpt_analyzer.py)

#### 新メソッド: `check_discrepancies_with_lc()`

```python
def check_discrepancies_with_lc(
    self,
    lc_analysis: Dict[str, Any],
    other_files_analyses: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Letter of Credit を基準に、関連書類のディスクレパンシーをチェック

    10項目の詳細チェックを実施し、以下を返す：
    - checks: 各項目のチェック結果
    - summary: 全体評価
    - critical_issues: 重大な問題
    - warnings: 警告
    - recommendations: 推奨事項
    """
```

#### 特徴

- L/C を基準に 10 項目を詳細チェック
- セマンティック的な相違判定
- JSON で構造化された結果を返す
- 各呼び出し前に 1 秒遅延を実装

### Frontend 修正 (src/app.py)

#### セッションステート変更

```python
# 変更前
st.session_state.uploaded_file_1, uploaded_file_2
st.session_state.analysis_result_1, analysis_result_2
st.session_state.comparison_result

# 変更後
st.session_state.uploaded_lc              # L/C ファイル
st.session_state.uploaded_other_files     # 複数ファイル
st.session_state.lc_analysis_result
st.session_state.other_files_analysis_results
st.session_state.discrepancy_check_result
```

#### 新機能関数

1. **`analyze_documents()`** (完全書き替え)
   - L/C 分析 → 検証
   - 複数ファイル順次分析
   - ディスクレチェック実行

2. **`display_discrepancy_results()`** (新規)
   - L/C 情報表示
   - 複数ファイル情報（タブ表示）
   - 10 項目のチェック結果（色分け）
   - Critical Issues/Warnings
   - Recommendations

---

## 📊 処理フロー

```
[L/C ファイルアップロード] + [複数ファイルアップロード]
            ↓
[🔍 Analyze & Check Discrepancies]
            ↓
┌─ L/C 分析・検証
│  ├─ OCR 抽出 (Document Intelligence)
│  ├─ 種別判定 (GPT: 1秒遅延)
│  ├─ フィールド抽出 (GPT: 1秒遅延)
│  └─ L/C 検証 (Letter of Credit か確認)
│
├─ 複数ファイル順次分析
│  ├─ ファイル1: 分析 (1秒遅延)
│  ├─ ファイル2: 分析 (1秒遅延)
│  └─ ...
│
└─ ディスクレチェック実行
   ├─ 10 項目詳細分析 (GPT: 1秒遅延)
   └─ 結果表示 (色分け表示)
```

---

## 🎨 UI レイアウト

**アップロード画面:**

```
┌──────────────────┬────────────────────────┐
│ L/C (単一)       │ Other Docs (複数)       │
├──────────────────┼────────────────────────┤
│ [Upload L/C]     │ [Upload Multiple]       │
└──────────────────┴────────────────────────┘
[🔍 Analyze & Check] [🗑️ Clear All]
```

**結果表示:**

```
📑 Letter of Credit Information
   └─ [L/C フィールド: 2列表示]

📊 Other Documents Information
   ├─ [タブ1: Invoice]
   ├─ [タブ2: Bill of Lading]
   └─ [タブ3: その他]

🔍 Discrepancy Check Results (10 Key Items)
   ├─ ✅ Item 1: 船積日チェック
   ├─ ❌ Item 2: L/C有効期限
   ├─ ⚠️ Item 3: 呈示期限チェック
   ... (全10項目)

⚠️ Critical Issues & Summary
   ├─ [重大な問題のリスト]
   └─ [総合評価]

💡 Recommendations
   └─ [推奨事項のリスト]
```

---

## 📝 使用方法

1. **L/C ファイルをアップロード**
   - 左側に Letter of Credit PDF をアップロード

2. **関連書類をアップロード**
   - 右側に複数の書類（Invoice、B/L など）をアップロード

3. **分析開始**
   - 「🔍 Analyze & Check Discrepancies」をクリック

4. **結果確認**
   - L/C 情報の確認
   - 関連書類情報の確認（タブで切り替え）
   - 10 項目のディスクレチェック結果を確認
   - Critical Issues と Recommendations を確認

---

## ⏳ タイミング

- L/C 分類前: 1 秒遅延
- L/C 抽出前: 1 秒遅延
- 関連書類分析前: 各 1 秒遅延
- ディスクレチェック前: 1 秒遅延

**合計遅延**: ファイル数に応じて約 4～10 秒

---

## ✅ エラーハンドリング

- **L/C 検証エラー**: L/C 以外のファイルがアップロードされた場合、処理中断
- **空の応答エラー**: GPT から空の応答を受け取った場合、エラーメッセージを返す
- **JSON パースエラー**: JSON パース失敗時、マークダウン形式を除去して再試行

---

## 📊 ログ出力例

```
INFO:gpt_analyzer:⏳ Waiting 1 second before GPT classification call...
INFO:gpt_analyzer:💬 Calling GPT API with model: gpt-5-mini
INFO:gpt_analyzer:✅ GPT API Response received
INFO:gpt_analyzer:⏳ Waiting 1 second before GPT extraction call...
INFO:gpt_analyzer:✅ Information extraction completed
...
INFO:gpt_analyzer:⏳ Waiting 1 second before GPT discrepancy check call...
INFO:gpt_analyzer:🔍 Checking discrepancies with Letter of Credit as reference...
INFO:gpt_analyzer:✅ Discrepancy check completed
INFO:gpt_analyzer:   Items checked: 10
```

---

## 🔍 GPT の詳細チェックロジック

`compare_documents()` メソッドでGPTに投げるプロンプトの特徴：

1. **セマンティック理解**
   - 項目名が異なっても意味が同じ場合を認識
   - 書類の内容理解に基づいた判断

2. **複数の比較カテゴリ**
   - **identical**: 完全に同じ
   - **semantically_equivalent**: 意味が同じ（表記が異なる）
   - **discrepant**: 相違がある

3. **相違の理由付け**
   - 単なる値の相違だけでなく、なぜ相違しているのかを説明

---

## 🧪 テスト方法

1. **アプリ起動**

   ```bash
   streamlit run src/app.py
   ```

2. **テスト用PDFを準備**
   - 関連する2つの貿易書類（例：Invoice 2枚）

3. **アップロード**
   - 2つのファイルを順序にアップロード

4. **実行**
   - 「Analyze & Compare」をクリック

5. **確認**
   - 左右の並行表示が正しいか
   - ディスクレプスキー結果が正確か
   - サマリが適切か

---

## ⚠️ 注意事項

1. **処理時間**
   - 2つのファイルの処理 + 比較のため、単ファイル処理より時間がかかります
   - 各ファイル10-30秒、比較10-20秒程度

2. **API コスト**
   - 1回の実行で3回のGPT呼び出し（ファイル1、ファイル2、比較）

3. **サポート書類**
   - すべての書類タイプの比較に対応
   - 異なる種類の書類同士の比較も可能

---

## 📦 ファイル修正サマリ

| ファイル                   | 変更内容                            | 行数変更 |
| -------------------------- | ----------------------------------- | -------- |
| `src/app.py`               | 大幅改造（シングル→マルチファイル） | +150 行  |
| `src/gpt_analyzer.py`      | `compare_documents()` メソッド追加  | +110 行  |
| `src/document_analyzer.py` | 変更なし                            | 0 行     |
| `src/config.py`            | 変更なし                            | 0 行     |

---

## ✅ 検証済み

- ✅ Python 構文チェック（py_compile）
- ✅ モジュールインポート確認
- ✅ 関数・メソッド定義確認
- ✅ セッション状態管理確認

---

**更新日:** 2026年3月16日  
**バージョン:** 2.0 (Multi-file Analysis & Comparison)  
**ステータス:** 準備完了
