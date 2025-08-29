# Home Signal - クイックスタート

## 🎯 目的
GitHub API制限を回避して、社内PC→自宅PCのプログラム起動を実現

## ⚡ セットアップ（5分）

### 1. GitHubリポジトリ作成
```
1. GitHub.com → New repository
2. Repository name: home-signal
3. ✅ Private
4. ✅ Initialize with README
5. Create repository
```

### 2. リモート設定
```bash
cd C:\Users\Tenormusica\home-signal
git remote add origin https://github.com/YOUR_USERNAME/home-signal.git
git push -u origin master
```

### 3. 自宅PCで常駐開始
```bash
cd C:\Users\Tenormusica\home-signal
python watch_signal.py
```

## 🚀 使用方法

### 社内PCから（WebUI操作）
1. GitHub → home-signal リポジトリ
2. `signal/command.json` をクリック
3. ✏️ Edit this file
4. 内容を変更:
```json
{
  "action": "start_program",
  "pane": "upper",
  "payload": ""
}
```
5. 🟢 Commit changes

### 自宅PC側の反応
- 10秒以内にClaude Codeが最前面に移動
- コンソールに実行ログが表示

## 📋 アクション一覧

| action | 動作 |
|--------|------|
| `start_program` | Claudeを最前面化 + payload実行 |
| `bring_front` | Claudeウィンドウ最前面化のみ |
| `run_script` | payloadのスクリプト実行 |
| `noop` | 何もしない |

## 🔧 環境変数
- `POLL_SEC=30` (監視間隔を30秒に変更)

## ✅ テスト方法
```bash
# ローカルテスト
python test_local.py

# 実際の動作確認
# 1. GitHubでcommand.jsonを編集
# 2. watch_signal.pyのコンソール出力を確認
```

## 💡 Tips
- ✅ API制限なし（git fetchのみ）
- ✅ プロキシ対応（git config設定）
- ✅ 重複実行防止（SHA記録）
- ✅ 最小リソース消費（10秒間隔）