#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试KDJ接口
"""

import requests
import json

def test_kdj_interface():
    """测试KDJ筛选接口"""
    base_url = "http://localhost:8000"
    
    print("=== 测试KDJ筛选接口 ===")
    
    # 测试新的接口路径
    url = f"{base_url}/api/stock/filter/kdj"
    params = {
        "j_threshold": 15.0,
        "limit": 5
    }
    
    try:
        print(f"请求URL: {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应成功: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get("value"):
                stocks = data["value"]
                print(f"\n找到 {len(stocks)} 只J值小于等于15的股票:")
                for i, stock in enumerate(stocks, 1):
                    print(f"{i}. {stock['code']} - {stock['name']} - J值: {stock['j_value']}")
            else:
                print("未找到满足条件的股票")
        else:
            print(f"请求失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("连接失败：请确保服务器正在运行")
    except requests.exceptions.Timeout:
        print("请求超时")
    except Exception as e:
        print(f"测试失败: {e}")

def test_available_routes():
    """测试可用的路由"""
    base_url = "http://localhost:8000"
    
    print("\n=== 测试可用路由 ===")
    
    # 测试根路径
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"根路径 /: {response.status_code}")
    except:
        print("根路径 /: 连接失败")
    
    # 测试股票列表接口
    try:
        response = requests.get(f"{base_url}/api/stock/list", timeout=5)
        print(f"股票列表 /api/stock/list: {response.status_code}")
    except:
        print("股票列表 /api/stock/list: 连接失败")
    
    # 测试KDJ筛选接口
    try:
        response = requests.get(f"{base_url}/api/stock/filter/kdj", timeout=5)
        print(f"KDJ筛选 /api/stock/filter/kdj: {response.status_code}")
    except:
        print("KDJ筛选 /api/stock/filter/kdj: 连接失败")

if __name__ == "__main__":
    test_available_routes()
    test_kdj_interface() 