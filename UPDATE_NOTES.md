# 機能更新メモ (2026年3月16日)

## 📋 更新内容 - 複数ファイル分析・比較機能の実装

### ✨ 新機能

#### 1. 2つのファイル同時分析

- 2つのPDFファイルを同時にアップロード可能
- 各ファイルを個別に処理（Document Intelligence → GPT分析）
- 処理は順序実行（ファイル1 → ファイル2）

#### 2. 並行表示（Side-by-Side Display）

- 抽出された項目情報を左右（50%/50%）に表示
- 各ファイルの情報が1列で整理されて表示

#### 3. ディスクレプスキー（相違点）チェック

- 2つのファイルの抽出項目を自動比較
- **緑字**: 一致する項目と値
- **赤字**: 一致しない項目と値
- 項目名が異なってもセマンティック的に同じ場合を認識

#### 4. 比較結果のサマリ

- 一致項目の表示
- 相違項目の表示と相違の理由
- 各ファイル特有の項目の表示
- GPTによる全体的なサマリをNotes として出力

---

## 🔧 実装内容

### Backend 修正 (src/gpt_analyzer.py)

#### 新メソッド: `compare_documents()`

```python
def compare_documents(self, doc1_analysis: Dict[str, Any], doc2_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    2つのドキュメント分析結果を比較

    処理フロー:
    1. 2つのファイルから抽出されたフィールド情報を取得
    2. フィールド情報をJSONで整形
    3. GPTに投げて、セマンティック的な比較を実施
    4. 以下の結果を返す:
       - matching_items: 一致する項目（identical または semantically_equivalent）
       - discrepant_items: 相違する項目と相違の理由
       - unique_to_doc1: ファイル1にのみ存在する項目
       - unique_to_doc2: ファイル2にのみ存在する項目
       - summary: 全体的なサマリ
    """
```

**特徴:**

- 項目名の相違を考慮（セマンティック比較）
- 書類内容の理解に基づいた相違判定
- JSONで構造化された結果を返す

### Frontend 修正 (src/app.py)

#### セッションステート拡張

```python
st.session_state.uploaded_file_1         # ファイル1
st.session_state.uploaded_file_2         # ファイル2
st.session_state.analysis_result_1       # ファイル1の分析結果
st.session_state.analysis_result_2       # ファイル2の分析結果
st.session_state.comparison_result       # 比較結果
```

#### 新機能関数

1. **`analyze_single_document(file, is_doc_1=True)`**
   - 1つのファイルを分析（OCR → GPT抽出）
   - エラーハンドリング実装

2. **`analyze_documents()`**
   - ファイル1を分析
   - ファイル2を分析
   - 比較実行
   - 結果を保存

3. **`display_comparison_results()`**
   - 並行表示（Document Type）
   - 並行表示（Extracted Fields）
   - 並行表示（Summary Notes）
   - ディスクレプスキー結果表示（緑/赤）
   - 一意な項目表示
   - 比較サマリ表示

#### UI レイアウト変更

**アップロード画面:**

```
[Document 1]          [Document 2]
[File Upload 1]       [File Upload 2]

[Analyze & Compare]   [Clear All]
```

**結果表示画面:**

```
=== Document Types ===
[Doc 1 Type]          [Doc 2 Type]

=== Extracted Information ===
[Doc 1 Fields]        [Doc 2 Fields]

=== Summary Notes ===
[Doc 1 Notes]         [Doc 2 Notes]

=== Discrepancy Check Results ===
✅ Matching Items (Green)
- [Field]: [Value] = [Field]: [Value]

❌ Discrepant Items (Red)
- [Field]: [Value] ≠ [Field]: [Value]
  Reason: ...

📋 Items Unique to Each Document
[Unique to Doc 1]     [Unique to Doc 2]

📌 Comparison Summary
[GPT-generated summary]
```

---

## 📊 処理フロー

```
┌─────────────────────┐
│  ファイル1 + ファイル2  │
└──────────┬──────────┘
           │
      ┌────▼────┐
      │ Upload  │
      └────┬────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼───┐    ┌───▼───┐
│File 1 │    │File 2 │
└───┬───┘    └───┬───┘
    │             │
    ▼             ▼
[Document Intelligence]
  Extract Text/Tables
    │             │
    └─────┬───────┘
          ▼
   [GPT Analysis]
   - Classify Type
   - Extract Fields
    │             │
    └─────┬───────┘
          ▼
  [Comparison Module]
  compare_documents()
    │
    ├─ Matching Items
    ├─ Discrepant Items
    ├─ Unique Items
    └─ Summary
          │
          ▼
    [Display Results]
    - Side-by-side
    - Color coded
    - Summarized
```

---

## 🎨 UIの変更点

### 旧UI（シングルファイル）

- ✅ ファイルアップロード（1つ）
- ✅ 分析ボタン
- ✅ 結果表示（1つの書類）

### 新UI（マルチファイル + 比較）

- ✅ ファイルアップロード（2つ）
- ✅ 分析 & 比較ボタン
- ✅ クリアボタン
- ✅ 並行結果表示（2つの書類）
- ✅ ディスクレプスキー結果表示
  - 緑字（一致）
  - 赤字（相違）
  - 黄字（一意）
- ✅ 比較サマリ

---

## 📝 使用方法

1. **2つのファイルをアップロード**
   - Document 1 アップロード領域にファイル1をアップロード
   - Document 2 アップロード領域にファイル2をアップロード

2. **分析開始**
   - 「🔍 Analyze & Compare」ボタンをクリック
   - システムが自動で分析と比較を実行

3. **結果確認**
   - 抽出項目を左右で確認
   - Notes（サマリ）を左右で確認
   - ディスクレプスキー結果を確認
   - 比較サマリを確認

4. **クリア**
   - 「🗑️ Clear All」ボタンでリセット

---

## 🔍 GPTの比較ロジック

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
