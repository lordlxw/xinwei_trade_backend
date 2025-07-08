# KDJ筛选接口使用说明

## 接口概述

本接口用于根据KDJ技术指标的J值筛选股票，满足您的量化交易策略需求。

## 接口详情

### 接口地址
```
GET /api/stock/filter/kdj
```

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| j_threshold | float | 否 | 15.0 | J值阈值，筛选J值小于等于此值的股票 |
| limit | int | 否 | 100 | 返回结果数量限制 |

### 请求示例

#### 筛选J值小于等于15的股票（默认）
```bash
curl "http://localhost:8000/api/stock/filter/kdj"
```

#### 筛选J值小于等于10的股票，限制返回20只
```bash
curl "http://localhost:8000/api/stock/filter/kdj?j_threshold=10&limit=20"
```

#### 筛选J值小于等于20的股票
```bash
curl "http://localhost:8000/api/stock/filter/kdj?j_threshold=20"
```

### 响应格式

```json
{
  "code": "00000",
  "message": "成功筛选出X只J值小于等于Y的股票",
  "value": [
    {
      "code": "000001",
      "name": "平安银行",
      "trade_date": "2024-01-15T00:00:00",
      "k_value": 25.5,
      "d_value": 30.2,
      "j_value": 12.3,
      "close_price": 15.80,
      "volume": 1234567.0,
      "turnover_rate": 2.5
    }
  ]
}
```

### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | string | 股票代码 |
| name | string | 股票名称 |
| trade_date | datetime | 交易日期 |
| k_value | float | KDJ的K值 |
| d_value | float | KDJ的D值 |
| j_value | float | KDJ的J值 |
| close_price | float | 收盘价 |
| volume | float | 成交量 |
| turnover_rate | float | 换手率 |

## 使用场景

### 1. 超卖信号筛选
当J值小于等于15时，通常表示股票处于超卖状态，可能存在反弹机会。

### 2. 自定义阈值筛选
您可以根据自己的策略调整J值阈值：
- J值 ≤ 10：极度超卖
- J值 ≤ 15：超卖
- J值 ≤ 20：接近超卖

### 3. 批量筛选
通过limit参数控制返回的股票数量，避免数据过多影响性能。

## 测试示例

运行测试脚本：
```bash
python test_kdj_filter.py
```

## 注意事项

1. 确保数据库中有足够的股票数据和技术指标数据
2. J值越小，筛选出的股票越少，但超卖信号越强
3. 建议结合其他技术指标和基本面分析进行投资决策
4. 接口返回的数据按J值升序排列，J值最小的股票排在前面

## 错误处理

如果出现错误，响应格式如下：
```json
{
  "code": "00001",
  "message": "错误描述",
  "value": null
}
```

常见错误：
- 数据库连接失败
- 没有找到满足条件的股票
- 参数格式错误 