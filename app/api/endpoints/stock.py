from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.services.data_service import data_service
from app.models.stock import Stock, StockDaily, StockIndicator
from app.utils.response_util import api_response
from pydantic import BaseModel

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