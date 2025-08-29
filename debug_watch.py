#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
watch_signal.py のデバッグ版 - エラーの詳細を表示
"""

import json
import subprocess
import time
import os
import sys
import pathlib

REPO_DIR = pathlib.Path(__file__).resolve().parent
SIGNAL_FILE = REPO_DIR / "signal" / "command.json"
STATE_FILE = REPO_DIR / ".last_processed_sha.txt"
POLL_SEC = 5  # デバッグ用に短縮

def safe_git(*args):
    """Gitコマンドを安全に実行"""
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_DIR)] + list(args),
            capture_output=True, 
            text=True, 
            check=False,
            timeout=30  # 30秒でタイムアウト
        )
        print(f"[git] {' '.join(args)} -> {result.returncode}")
        if result.stderr and result.returncode != 0:
            print(f"[git-err] {result.stderr.strip()}")
        return result
    except subprocess.TimeoutExpired:
        print(f"[git-timeout] Command timed out: {args}")
        return subprocess.CompletedProcess(args, 1, "", "Timeout")
    except Exception as e:
        print(f"[git-exception] {e}")
        return subprocess.CompletedProcess(args, 1, "", str(e))

def debug_current_sha():
    result = safe_git("rev-parse", "HEAD")
    return result.stdout.strip() if result.returncode == 0 else ""

def debug_remote_sha():
    print("[fetch] Attempting git fetch...")
    
    # リモート設定確認
    url_result = safe_git("remote", "get-url", "origin")
    if url_result.returncode == 0:
        print(f"[remote] Origin URL: {url_result.stdout.strip()}")
    else:
        print("[remote] No origin configured")
        return ""
    
    # Fetch実行
    fetch_result = safe_git("fetch", "--depth=1", "origin", "main")
    if fetch_result.returncode != 0:
        print(f"[fetch-error] Failed to fetch: {fetch_result.stderr}")
        return ""
    
    # Remote SHAを取得
    sha_result = safe_git("rev-parse", "origin/main")
    return sha_result.stdout.strip() if sha_result.returncode == 0 else ""

def debug_signal_processing():
    """シグナルファイル処理のデバッグ"""
    print(f"[signal] File exists: {SIGNAL_FILE.exists()}")
    if not SIGNAL_FILE.exists():
        return None
    
    try:
        content = SIGNAL_FILE.read_text(encoding='utf-8')
        print(f"[signal] Raw content: {content}")
        
        cmd = json.loads(content)
        print(f"[signal] Parsed JSON: {cmd}")
        return cmd
    except Exception as e:
        print(f"[signal-error] Failed to parse: {e}")
        return None

def debug_main():
    print("=== Home Signal Debug Mode ===")
    print(f"Repository: {REPO_DIR}")
    print(f"Poll interval: {POLL_SEC}s")
    print()
    
    # 初期状態確認
    current = debug_current_sha()
    print(f"[init] Current SHA: {current[:8] if current else 'None'}")
    
    last_processed = ""
    if STATE_FILE.exists():
        last_processed = STATE_FILE.read_text(encoding='utf-8').strip()
        print(f"[init] Last processed: {last_processed[:8] if last_processed else 'None'}")
    
    # メインループ（3回だけ実行してテスト）
    for i in range(3):
        print(f"\n--- Loop {i+1}/3 ---")
        
        try:
            # リモートSHA取得
            remote = debug_remote_sha()
            if not remote:
                print("[skip] No remote SHA available")
                time.sleep(POLL_SEC)
                continue
                
            print(f"[check] Remote SHA: {remote[:8]}")
            
            # ローカルとの比較
            current = debug_current_sha()
            print(f"[check] Current SHA: {current[:8]}")
            
            if remote != current:
                print("[sync] SHA mismatch - updating local")
                safe_git("reset", "--hard", "origin/main")
                current = debug_current_sha()
                print(f"[sync] Updated to: {current[:8]}")
            
            # 処理済みかチェック
            if remote == last_processed:
                print("[skip] Already processed")
            else:
                # シグナル処理
                cmd = debug_signal_processing()
                if cmd:
                    print(f"[execute] Action: {cmd.get('action')}")
                    print(f"[execute] Payload: {cmd.get('payload')}")
                    
                    # 実際のアクションは実行しない（デバッグモード）
                    print("[execute] (Skipped in debug mode)")
                    
                    # 状態更新
                    STATE_FILE.write_text(remote, encoding='utf-8')
                    last_processed = remote
                    print(f"[state] Updated last processed to: {remote[:8]}")
                else:
                    print("[skip] No valid command found")
            
        except KeyboardInterrupt:
            print("\n[exit] Interrupted by user")
            break
        except Exception as e:
            print(f"[error] {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"[wait] Sleeping {POLL_SEC}s...")
        time.sleep(POLL_SEC)
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_main()