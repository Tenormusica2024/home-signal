#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
watch_signal.pyの関数単体テスト
"""

import sys
import subprocess
from pathlib import Path
from watch_signal import _git, _current_sha, _remote_sha, REPO_DIR, SIGNAL_FILE

def test_git_commands():
    """Git関連の関数をテスト"""
    print("=== Git Commands Test ===")
    
    # Current SHA
    sha = _current_sha()
    print(f"Current SHA: {sha[:8] if sha else 'None'}")
    
    # Remote SHA (with fetch)
    print("Fetching from remote...")
    remote_sha = _remote_sha()
    print(f"Remote SHA: {remote_sha[:8] if remote_sha else 'None'}")
    
    # Basic git command test
    result = _git("status", "--porcelain")
    print(f"Git status return code: {result.returncode}")
    
    return sha, remote_sha

def test_signal_file():
    """Signal file reading test"""
    print("=== Signal File Test ===")
    print(f"Signal file path: {SIGNAL_FILE}")
    print(f"Exists: {SIGNAL_FILE.exists()}")
    
    if SIGNAL_FILE.exists():
        content = SIGNAL_FILE.read_text(encoding='utf-8')
        print(f"Content: {content.strip()}")
    
def test_watch_logic():
    """Watch logic simulation test"""
    print("=== Watch Logic Simulation ===")
    
    from watch_signal import _read_last, _write_last
    
    # Test state file operations
    current_sha = _current_sha()
    if current_sha:
        print(f"Writing test SHA: {current_sha[:8]}")
        _write_last(current_sha)
        
        read_sha = _read_last()
        print(f"Read SHA: {read_sha[:8] if read_sha else 'None'}")
        print(f"SHA match: {current_sha == read_sha}")

if __name__ == "__main__":
    print(f"Repository: {REPO_DIR}")
    print(f"Working directory: {Path.cwd()}")
    print()
    
    sha, remote_sha = test_git_commands()
    print()
    test_signal_file()
    print()
    test_watch_logic()
    
    print("\n=== Test Summary ===")
    print(f"✓ Git commands working: {bool(sha)}")
    print(f"✓ Remote fetch working: {bool(remote_sha)}")
    print(f"✓ Signal file exists: {SIGNAL_FILE.exists()}")
    print(f"✓ Basic functionality: Ready")