import akshare as ak

# 获取沪深京所有A股的基础信息
df = ak.stock_info_a_code_name()
print(df)