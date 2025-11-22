# Gemini APIモデル名エラー分析

## エラー内容
```
404 models/gemini-pro is not found for API version v1beta
```

## 原因

### 1. 古いモデル名を使用
- ❌ `gemini-pro` - 廃止済み
- ✅ `gemini-1.5-pro` - 最新
- ✅ `gemini-1.5-flash` - 高速版

### 2. Gemini APIバージョンの変更
- v1beta API では gemini-pro が利用不可
- 新しいモデル名に移行が必要

## 正しいモデル名

### 推奨モデル
1. **gemini-1.5-pro** (推奨)
   - 最も高性能
   - 長いコンテキスト対応
   - 複雑なタスクに最適

2. **gemini-1.5-flash** (高速)
   - 高速処理
   - コスト効率が良い
   - シンプルなタスク向け

3. **gemini-2.0-flash-exp** (実験版)
   - 最新機能
   - 実験的機能を試せる

## 既存システムの確認

既存のTaskExecutorやF1エージェントで動作しているモデル名を確認し、
それに合わせる必要があります。

