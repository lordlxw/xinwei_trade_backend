import akshare as ak
import pandas as pd

def calculate_kdj(df, n=9):
    """
    同花顺风格KDJ算法，参数9,3,3，初始K/D=50，递推
    """
    low_list = df['最低'].rolling(window=n, min_periods=1).min()
    high_list = df['最高'].rolling(window=n, min_periods=1).max()
    rsv = (df['收盘'] - low_list) / (high_list - low_list) * 100

    k = [50]
    d = [50]
    for i in range(1, len(df)):
        k.append((2/3) * k[-1] + (1/3) * rsv.iloc[i])
        d.append((2/3) * d[-1] + (1/3) * k[-1])
    df['K'] = k
    df['D'] = d
    df['J'] = 3 * df['K'] - 2 * df['D']
    return df

if __name__ == "__main__":
    code = "600318"
    start_date = "20240101"
    end_date = "20250625"
    print(f"拉取股票{code}的日K线数据，区间：{start_date} - {end_date}")
    df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
    print("原始数据前5行：")
    print(df.head())
    print(f"共{len(df)}条数据，列名：{list(df.columns)}")

    # 计算KDJ
    df = calculate_kdj(df, n=9)
    print("带KDJ的前5行：")
    print(df[['日期', '收盘', '最高', '最低', 'K', 'D', 'J']].head(15))

    # 保存为csv
    df.to_csv(f"{code}_akshare_qfq_with_kdj.csv", index=False, encoding="utf-8-sig")
    print(f"已保存为 {code}_akshare_qfq_with_kdj.csv")