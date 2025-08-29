# Home Signal - API制限回避型リモート起動システム

## 概要
GitHub API制限を回避して、Git fetchのみで自宅PCのプログラムをリモート起動するシステムです。

## 仕組み
- 社内PC: GitHub WebUIで `signal/command.json` を編集→コミット
- 自宅PC: `watch_signal.py` がgit fetchで変更検知→プログラム起動

## セットアップ

### 1. GitHub設定
1. GitHubで新しいプライベートリポジトリ `home-signal` を作成
2. このローカルリポジトリをpush:
```bash
git remote add origin https://github.com/YOUR_USERNAME/home-signal.git
git add .
git commit -m "Initial setup"
git push -u origin main
```

### 2. 自宅PCでの起動
```bash
cd C:\Users\Tenormusica\home-signal
python watch_signal.py
```

## 使用方法

### 社内PCから（GitHub WebUI）
1. `signal/command.json` を開く
2. 内容を編集:
```json
{
  "action": "start_program",
  "pane": "upper", 
  "payload": "C:\\path\\to\\script.py"
}
```
3. "Commit changes" をクリック

### 利用可能なアクション
- `start_program`: Claudeプロセスを最前面に、payloadがあれば実行
- `bring_front`: Claudeウィンドウを最前面に
- `run_script`: payloadで指定されたスクリプトを実行
- `noop`: 何もしない

### 環境変数
- `POLL_SEC`: 監視間隔（デフォルト10秒）

## 特徴
- ✅ GitHub REST API不要（git fetchのみ）
- ✅ API制限の影響を受けない
- ✅ プライベートリポジトリで安全
- ✅ 同一コミットの重複実行防止
- ✅ プロキシ対応（git configで設定）