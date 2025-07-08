#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试获取单个股票的KDJ值
"""

import requests
import json

def get_stock_kdj(stock_code):
    """获取指定股票的KDJ值"""
    base_url = "http://localhost:8000"
    
    print(f"=== 获取股票 {stock_code} 的KDJ值 ===")
    
    # 方法1：获取最新数据
    url1 = f"{base_url}/api/stock/{stock_code}/latest"
    
    try:
        print(f"请求URL: {url1}")
        response = requests.get(url1, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get("value") and data["value"].get("indicator"):
                indicator = data["value"]["indicator"]
                print(f"\n股票 {stock_code} 的最新KDJ值:")
                print(f"K值: {indicator.k_value}")
                print(f"D值: {indicator.d_value}")
                print(f"J值: {indicator.j_value}")
                print(f"交易日期: {indicator.trade_date}")
            else:
                print("未找到KDJ数据")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

def get_stock_indicators_history(stock_code, limit=5):
    """获取指定股票的历史KDJ数据"""
    base_url = "http://localhost:8000"
    
    print(f"\n=== 获取股票 {stock_code} 的历史KDJ数据 ===")
    
    url = f"{base_url}/api/stock/{stock_code}/indicators"
    params = {"limit": limit}
    
    try:
        print(f"请求URL: {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get("value"):
                indicators = data["value"]
                print(f"\n股票 {stock_code} 最近 {len(indicators)} 天的KDJ数据:")
                for i, indicator in enumerate(indicators, 1):
                    print(f"{i}. 日期: {indicator.trade_date}")
                    print(f"   K值: {indicator.k_value}")
                    print(f"   D值: {indicator.d_value}")
                    print(f"   J值: {indicator.j_value}")
                    print()
            else:
                print("未找到历史KDJ数据")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

def update_stock_data(stock_code):
    """更新指定股票的数据"""
    base_url = "http://localhost:8000"
    
    print(f"\n=== 更新股票 {stock_code} 的数据 ===")
    
    url = f"{base_url}/api/stock/{stock_code}/update"
    
    try:
        print(f"请求URL: {url}")
        response = requests.post(url, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    stock_code = "605499"  # 您要查询的股票代码
    
    # 1. 获取最新KDJ值
    get_stock_kdj(stock_code)
    
    # 2. 获取历史KDJ数据
    get_stock_indicators_history(stock_code, limit=3)
    
    # 3. 如果需要更新数据，取消下面的注释
    # update_stock_data(stock_code) 