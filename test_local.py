#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ローカルテスト用スクリプト
GitHubリモートなしでwatch_signal.pyの動作をテストします
"""

import json
import time
from watch_signal import _handle_action, SIGNAL_FILE

def test_actions():
    """異なるアクションをテストします"""
    test_cases = [
        {
            "action": "noop",
            "pane": "",
            "payload": "No operation test"
        },
        {
            "action": "start_program", 
            "pane": "upper",
            "payload": ""
        },
        {
            "action": "bring_front",
            "pane": "",
            "payload": ""
        }
    ]
    
    for i, test_cmd in enumerate(test_cases):
        print(f"\n=== Test {i+1}: {test_cmd['action']} ===")
        print(f"Command: {test_cmd}")
        
        # signal/command.jsonを更新
        with open(SIGNAL_FILE, 'w', encoding='utf-8') as f:
            json.dump(test_cmd, f, indent=2)
            
        # アクションを実行
        _handle_action(test_cmd)
        print(f"✅ Test {i+1} completed")
        time.sleep(1)

if __name__ == "__main__":
    print("Home Signal Local Test")
    print(f"Signal file: {SIGNAL_FILE}")
    
    test_actions()
    
    # 元の状態に戻す
    original_cmd = {
        "action": "noop",
        "pane": "",
        "payload": "Test completed"
    }
    with open(SIGNAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(original_cmd, f, indent=2)
        
    print("\nAll tests completed! Signal file reset to noop.")