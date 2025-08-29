#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub APIを使わず、git fetchのみで合図ファイルの更新を検知してローカル動作させる最小ウォッチャ
- 監視対象: signal/command.json
- 同一コミットは再処理しない（最後に処理したSHAを記録）
- 起動する処理は _handle_action() 内で分岐
"""

import json, subprocess, time, os, sys, pathlib, psutil

REPO_DIR = pathlib.Path(__file__).resolve().parent
SIGNAL_FILE = REPO_DIR / "signal" / "command.json"
STATE_FILE  = REPO_DIR / ".last_processed_sha.txt"
POLL_SEC    = int(os.getenv("POLL_SEC", "10"))  # 10〜30秒程度で十分

def _git(*args):
    return subprocess.run(["git", "-C", str(REPO_DIR), *args],
                          capture_output=True, text=True, check=False)

def _current_sha():
    r = _git("rev-parse", "HEAD")
    return r.stdout.strip() if r.returncode == 0 else ""

def _remote_sha():
    # upstreamが無い場合は設定
    _git("remote", "set-url", "origin", _git("remote", "get-url", "origin").stdout.strip())
    _git("fetch", "--depth=1", "origin", "main")
    r = _git("rev-parse", "origin/main")
    return r.stdout.strip() if r.returncode == 0 else ""

def _checkout_origin_main():
    # 初回 or 乖離時は origin/main に合わせる（ローカル変更なし前提）
    _git("reset", "--hard", "origin/main")

def _read_last():
    return STATE_FILE.read_text(encoding="utf-8").strip() if STATE_FILE.exists() else ""

def _write_last(sha):
    STATE_FILE.write_text(sha, encoding="utf-8")

def _handle_action(cmd: dict):
    action = (cmd.get("action") or "").lower()
    pane   = (cmd.get("pane") or "").lower()    # 使わないなら無視してOK
    payload= cmd.get("payload")

    print(f"[action] {action} pane={pane} payload={payload}")

    # ここに"家PCで起動したい処理"を書く（最小：プログラム起動）
    if action == "start_program":
        # Claude Codeプロセスを確認して最前面に持ってくる例
        claude_processes = [p for p in psutil.process_iter(attrs=["name", "pid"]) 
                           if p.info["name"] and "claude" in p.info["name"].lower()]
        
        if claude_processes:
            print(f"[info] Found Claude processes: {[p.info['name'] for p in claude_processes]}")
            # Windowsでウィンドウを最前面に持ってくる（PowerShell利用）
            subprocess.run([
                "powershell", "-Command", 
                "Add-Type -AssemblyName Microsoft.VisualBasic; "
                "[Microsoft.VisualBasic.Interaction]::AppActivate('Claude')"
            ], check=False)
        else:
            print("[warn] Claude process not found")
            
        # 特定のプログラムを起動したい場合（例：メモ帳）
        if payload and payload.strip():
            subprocess.Popen(["notepad", payload.strip()], shell=False)

    elif action == "bring_front":
        # Claude Codeウィンドウを最前面に
        subprocess.run([
            "powershell", "-Command", 
            "Add-Type -AssemblyName Microsoft.VisualBasic; "
            "[Microsoft.VisualBasic.Interaction]::AppActivate('Claude')"
        ], check=False)

    elif action == "run_script":
        # 既存スクリプトを実行
        if payload:
            script_path = REPO_DIR / payload
            if script_path.exists():
                subprocess.Popen([sys.executable, str(script_path)], shell=False)

    elif action == "noop":
        pass  # 何もしない

    # 必要になればアクション増やす:
    # - "toggle": 設定トグル など

def main():
    print(f"[watch] repo={REPO_DIR} poll={POLL_SEC}s")
    last = _read_last()

    while True:
        try:
            remote = _remote_sha()
            if not remote:
                print("[wait] No remote SHA, retrying...")
                time.sleep(POLL_SEC)
                continue

            if remote != _current_sha():
                print(f"[sync] Updating to {remote}")
                _checkout_origin_main()

            if remote != last and SIGNAL_FILE.exists():
                try:
                    cmd = json.loads(SIGNAL_FILE.read_text(encoding="utf-8"))
                except Exception as e:
                    print(f"[warn] invalid JSON: {e}")
                    _write_last(remote)
                    time.sleep(POLL_SEC)
                    continue

                print(f"[exec] new signal @ {remote}: {cmd}")
                _handle_action(cmd)
                _write_last(remote)
            else:
                if remote == last:
                    print(f"[skip] Already processed {remote[:8]}")
                else:
                    print(f"[wait] No signal file yet")
                    
            time.sleep(POLL_SEC)
        except KeyboardInterrupt:
            print("[exit] Interrupted by user")
            break
        except Exception as e:
            print(f"[err] {type(e).__name__}: {e}")
            time.sleep(max(10, POLL_SEC))

if __name__ == "__main__":
    main()