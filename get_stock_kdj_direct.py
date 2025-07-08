#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接使用akshare获取股票的KDJ值
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def calculate_kdj(df, n=9, m1=3, m2=3):
    """计算KDJ指标，直接用中文列名"""
    try:
        low_list = df['最低'].rolling(window=n, min_periods=1).min()
        high_list = df['最高'].rolling(window=n, min_periods=1).max()
        rsv = (df['收盘'] - low_list) / (high_list - low_list) * 100

        k = [50.0]
        d = [50.0]
        for i in range(1, len(df)):
            rsv_value = float(rsv.iloc[i]) if pd.notna(rsv.iloc[i]) else 50.0
            k.append((2/3) * k[-1] + (1/3) * rsv_value)
            d.append((2/3) * d[-1] + (1/3) * k[-1])
        df['k_value'] = k
        df['d_value'] = d
        df['j_value'] = 3 * df['k_value'] - 2 * df['d_value']
        return df
    except Exception as e:
        print(f"计算KDJ失败: {e}")
        return df

def get_stock_kdj(stock_code):
    """获取指定股票的KDJ值"""
    print(f"=== 获取股票 {stock_code} 的KDJ值 ===")
    
    try:
        # 获取股票数据
        print("正在获取股票数据...")
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                               start_date=(datetime.now() - timedelta(days=60)).strftime('%Y%m%d'),
                               end_date=datetime.now().strftime('%Y%m%d'), 
                               adjust="qfq")
        
        if df.empty:
            print(f"未获取到股票 {stock_code} 的数据")
            return
        
        print(f"成功获取 {len(df)} 条数据")
        print(f"原始列名: {list(df.columns)}")
        print(df.head(3))
        
        # 计算KDJ
        print("正在计算KDJ指标...")
        df = calculate_kdj(df)
        
        # 显示最新数据
        latest = df.iloc[-1]
        print(f"\n股票 {stock_code} 最新KDJ值:")
        print(f"日期: {latest['日期']}")
        print(f"收盘价: {latest['收盘']:.2f}")
        print(f"K值: {latest['k_value']:.2f}")
        print(f"D值: {latest['d_value']:.2f}")
        print(f"J值: {latest['j_value']:.2f}")
        
        # 显示最近5天的KDJ数据
        print(f"\n最近5天的KDJ数据:")
        recent_data = df.tail(5)
        for _, row in recent_data.iterrows():
            print(f"日期: {row['日期']}, K: {row['k_value']:.2f}, D: {row['d_value']:.2f}, J: {row['j_value']:.2f}")
        
        return df
        
    except Exception as e:
        print(f"获取数据失败: {e}")

def analyze_kdj_signal(df):
    """分析KDJ信号"""
    if df is None or df.empty:
        return
    
    latest = df.iloc[-1]
    j_value = latest['j_value']
    k_value = latest['k_value']
    d_value = latest['d_value']
    
    print(f"\n=== KDJ信号分析 ===")
    print(f"当前J值: {j_value:.2f}")
    
    # 超卖信号
    if j_value <= 15:
        print("[超卖信号] J值 <= 15，可能存在反弹机会")
    elif j_value <= 20:
        print("[接近超卖] J值 <= 20，需要关注")
    else:
        print("[正常区间] J值 > 20")
    
    # KDJ金叉死叉
    if k_value > d_value:
        print("[金叉信号] K值 > D值，上涨趋势")
    else:
        print("[死叉信号] K值 < D值，下跌趋势")

if __name__ == "__main__":
    stock_code = "605499"  # 您要查询的股票代码
    
    # 获取KDJ数据
    df = get_stock_kdj(stock_code)
    
    # 分析KDJ信号
    if df is not None:
        analyze_kdj_signal(df) 