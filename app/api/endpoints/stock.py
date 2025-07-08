from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.services.data_service import data_service
from app.models.stock import Stock, StockDaily, StockIndicator
from app.utils.response_util import api_response
from pydantic import BaseModel
import akshare as ak
import pandas as pd
import typing as t
from fastapi.encoders import jsonable_encoder

router = APIRouter()

class StockInfo(BaseModel):
    code: str
    name: str
    industry: Optional[str] = None
    market: Optional[str] = None

class StockDailyData(BaseModel):
    code: str
    trade_date: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    amount: float
    turnover_rate: float

class StockIndicatorData(BaseModel):
    code: str
    trade_date: datetime
    k_value: float
    d_value: float
    j_value: float
    ma5: float
    ma10: float
    ma20: float

# 策略注册表
global STRATEGY_REGISTRY
STRATEGY_REGISTRY = {}

def register_strategy(name):
    def decorator(func):
        STRATEGY_REGISTRY[name] = func
        return func
    return decorator

@register_strategy('kdj_j_le')
def kdj_j_le(df, threshold=15):
    # 计算KDJ
    low_list = df['最低'].rolling(window=9, min_periods=1).min()
    high_list = df['最高'].rolling(window=9, min_periods=1).max()
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
    latest = df.iloc[-1]
    return latest['j_value'] <= threshold

@register_strategy('volume_down')
def volume_down(df, ratio=0.67):
    if len(df) < 2:
        return False
    today = df.iloc[-1]
    yesterday = df.iloc[-2]
    # 只判断量能减少，不判断绿柱
    if today['成交量'] >= yesterday['成交量']:
        return False
    if today['成交量'] > yesterday['成交量'] * ratio:
        return False
    return True

def check_strategies(df, strategy_config: t.List[dict]):
    for item in strategy_config:
        func = STRATEGY_REGISTRY[item['name']]
        if not func(df, **item.get('params', {})):
            return False
    return True

@router.get("/filter/kdj")
async def filter_kdj_stocks(
    j_threshold: float = Query(15.0, description="J值阈值"),
    limit: int = Query(100, description="返回数量限制")
):
    """
    只遍历60开头的A股，筛选KDJ中J值小于等于指定阈值的股票
    """
    stock_list = ak.stock_info_a_code_name()
    stock_list = stock_list[stock_list['code'].astype(str).str.startswith('60')]
    results = []

    for idx, row in stock_list.iterrows():
        code = str(row['code'])
        name = row['name']
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=(datetime.now() - timedelta(days=60)).strftime('%Y%m%d'),
                end_date=datetime.now().strftime('%Y%m%d'),
                adjust="qfq"
            )
            if df.empty:
                continue

            # 用中文列名计算KDJ
            low_list = df['最低'].rolling(window=9, min_periods=1).min()
            high_list = df['最高'].rolling(window=9, min_periods=1).max()
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

            latest = df.iloc[-1]
            if latest['j_value'] <= j_threshold:
                results.append({
                    "code": code,
                    "name": name,
                    "date": latest['日期'],
                    "close": latest['收盘'],
                    "k": round(latest['k_value'], 2),
                    "d": round(latest['d_value'], 2),
                    "j": round(latest['j_value'], 2)
                })
        except Exception as e:
            continue  # 某只股票出错跳过

    # 按J值升序排序，最多返回limit只
    results = sorted(results, key=lambda x: x['j'])[:limit]
    return {"count": len(results), "stocks": results}

@router.get("/list")
async def get_stock_list(db: Session = Depends(get_db)):
    """获取A股股票列表"""
    try:
        stock_list = data_service.get_stock_list()
        return api_response(value=stock_list)
    except Exception as e:
        return api_response(message=f"获取股票列表失败: {str(e)}", code="00001", value=None)

@router.get("/{code}/daily")
async def get_stock_daily_data(
    code: str,
    db: Session = Depends(get_db),
    limit: int = Query(30, description="返回数据条数")
):
    """获取股票日线数据"""
    try:
        daily_data = db.query(StockDaily).filter(
            StockDaily.code == code
        ).order_by(StockDaily.trade_date.desc()).limit(limit).all()
        return api_response(value=daily_data)
    except Exception as e:
        return api_response(message=f"获取股票日线数据失败: {str(e)}", code="00001", value=None)

@router.get("/{code}/indicators")
async def get_stock_indicators(
    code: str,
    db: Session = Depends(get_db),
    limit: int = Query(30, description="返回数据条数")
):
    """获取股票技术指标数据"""
    try:
        indicator_data = db.query(StockIndicator).filter(
            StockIndicator.code == code
        ).order_by(StockIndicator.trade_date.desc()).limit(limit).all()
        return api_response(value=indicator_data)
    except Exception as e:
        return api_response(message=f"获取股票技术指标失败: {str(e)}", code="00001", value=None)

@router.post("/{code}/update")
async def update_stock_data(
    code: str,
    db: Session = Depends(get_db)
):
    """更新股票数据"""
    try:
        # 获取股票数据
        df = data_service.get_stock_daily_data(code)
        if df is None or df.empty:
            return api_response(message=f"未找到股票{code}的数据", code="00001", value=None)
        
        # 计算技术指标
        df = data_service.calculate_kdj(df)
        df = data_service.calculate_ma(df)
        
        # 保存到数据库
        success = data_service.save_stock_data(db, code, df)
        if not success:
            return api_response(message="保存数据失败", code="00001", value=None)
        
        return api_response(message=f"股票{code}数据更新成功", value={"data_count": len(df)})
    except Exception as e:
        return api_response(message=f"更新股票数据失败: {str(e)}", code="00001", value=None)

@router.get("/{code}/latest")
async def get_stock_latest_data(
    code: str,
    db: Session = Depends(get_db)
):
    """获取股票最新数据"""
    try:
        latest_data = data_service.get_latest_data(db, code)
        if not latest_data:
            return api_response(message=f"未找到股票{code}的最新数据", code="00001", value=None)
        
        return api_response(value=latest_data)
    except Exception as e:
        return api_response(message=f"获取股票最新数据失败: {str(e)}", code="00001", value=None)

from app.utils.response_util import api_response
from fastapi.encoders import jsonable_encoder

@router.post("/filter/compound")
async def filter_compound_stocks(
    strategy_config: t.List[dict] = Body(..., description="策略组合配置"),
    limit: int = Query(100, description="返回数量限制")
):
    """
    多条件复合选股接口，支持策略组合和参数化。POST JSON: [{"name":策略名, "params":{参数}}]
    """
    stock_list = ak.stock_info_a_code_name()
    stock_list = stock_list[stock_list['code'].astype(str).str.startswith('60')]
    results = []

    for idx, row in stock_list.iterrows():
        code = str(row['code'])
        name = str(row['name'])
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=(datetime.now() - timedelta(days=60)).strftime('%Y%m%d'),
                end_date=datetime.now().strftime('%Y%m%d'),
                adjust="qfq"
            )
            if df.empty:
                continue
            if check_strategies(df, strategy_config):
                latest = df.iloc[-1]
                results.append({
                    "code": str(code),
                    "name": str(name),
                    "date": str(latest['日期']),
                    "close": float(latest['收盘']),
                    "k": float(round(latest.get('k_value', 0), 2)),
                    "d": float(round(latest.get('d_value', 0), 2)),
                    "j": float(round(latest.get('j_value', 0), 2)),
                    "volume": int(latest['成交量'])
                })
        except Exception as e:
            continue
    value = {"count": len(results), "stocks": results[:limit]}
    return api_response(message="复合选股成功", code="00000", value=value)


 