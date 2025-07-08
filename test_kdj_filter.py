#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试KDJ筛选接口
"""

import requests
import json

def test_kdj_filter():
    """测试KDJ筛选接口"""
    base_url = "http://localhost:8000"
    
    # 测试KDJ筛选接口
    print("=== 测试KDJ筛选接口 ===")
    
    # 测试J值小于等于15的股票
    url = f"{base_url}/api/stock/filter/kdj"
    params = {
        "j_threshold": 15.0,
        "limit": 20
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get("value"):
                stocks = data["value"]
                print(f"\n找到 {len(stocks)} 只J值小于等于15的股票:")
                for i, stock in enumerate(stocks[:10], 1):  # 只显示前10只
                    print(f"{i}. {stock['code']} - {stock['name']} - J值: {stock['j_value']}")
            else:
                print("未找到满足条件的股票")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

def test_kdj_filter_custom():
    """测试自定义J值阈值的KDJ筛选"""
    base_url = "http://localhost:8000"
    
    print("\n=== 测试自定义J值阈值 ===")
    
    # 测试不同的J值阈值
    thresholds = [10.0, 20.0, 30.0]
    
    for threshold in thresholds:
        url = f"{base_url}/api/stock/filter/kdj"
        params = {
            "j_threshold": threshold,
            "limit": 5
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                stocks = data.get("value", [])
                print(f"J值 <= {threshold}: 找到 {len(stocks)} 只股票")
            else:
                print(f"J值 <= {threshold}: 请求失败")
        except Exception as e:
            print(f"J值 <= {threshold}: 测试失败 - {e}")

if __name__ == "__main__":
    test_kdj_filter()
    test_kdj_filter_custom() 