from sqlalchemy import Column, String, Float, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Stock(Base):
    """股票基本信息表"""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, comment="股票代码")
    name = Column(String(50), comment="股票名称")
    industry = Column(String(100), comment="所属行业")
    market = Column(String(20), comment="市场类型(主板/创业板/科创板)")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class StockDaily(Base):
    """股票日线数据表"""
    __tablename__ = "stock_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), index=True, comment="股票代码")
    trade_date = Column(DateTime, index=True, comment="交易日期")
    open_price = Column(Float, comment="开盘价")
    high_price = Column(Float, comment="最高价")
    low_price = Column(Float, comment="最低价")
    close_price = Column(Float, comment="收盘价")
    volume = Column(Float, comment="成交量")
    amount = Column(Float, comment="成交额")
    turnover_rate = Column(Float, comment="换手率")
    created_at = Column(DateTime, default=datetime.now)

class StockIndicator(Base):
    """股票技术指标表"""
    __tablename__ = "stock_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), index=True, comment="股票代码")
    trade_date = Column(DateTime, index=True, comment="交易日期")
    k_value = Column(Float, comment="KDJ的K值")
    d_value = Column(Float, comment="KDJ的D值")
    j_value = Column(Float, comment="KDJ的J值")
    ma5 = Column(Float, comment="5日均线")
    ma10 = Column(Float, comment="10日均线")
    ma20 = Column(Float, comment="20日均线")
    rsi = Column(Float, comment="RSI指标")
    macd = Column(Float, comment="MACD指标")
    created_at = Column(DateTime, default=datetime.now)

 