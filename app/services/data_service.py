import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from loguru import logger
from sqlalchemy.orm import Session
from app.models.stock import Stock, StockDaily, StockIndicator
from app.core.config import settings

class DataService:
    """数据服务类，负责获取和处理股票数据"""
    
    def __init__(self):
        self.logger = logger
    
    def get_stock_list(self) -> List[Dict[str, Any]]:
        """获取A股股票列表"""
        try:
            self.logger.info("开始获取A股股票列表...")
            # 使用akshare获取A股股票列表
            stock_list = ak.stock_info_a_code_name()
            self.logger.info(f"成功获取 {len(stock_list)} 只股票")
            
            # 转换为字典格式
            result = []
            for _, row in stock_list.iterrows():
                result.append({
                    'code': row['code'],
                    'name': row['name']
                })
            
            return result
        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            # 返回一些测试用的股票代码
            return [
                {'code': '000001', 'name': '平安银行'},
                {'code': '000002', 'name': '万科A'},
                {'code': '000858', 'name': '五粮液'},
                {'code': '002415', 'name': '海康威视'},
                {'code': '600036', 'name': '招商银行'},
                {'code': '600519', 'name': '贵州茅台'},
                {'code': '000725', 'name': '京东方A'},
                {'code': '002594', 'name': '比亚迪'},
                {'code': '300059', 'name': '东方财富'},
                {'code': '600276', 'name': '恒瑞医药'}
            ]
    
    def get_stock_daily_data(self, code: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """获取股票日线数据"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            self.logger.info(f"获取股票{code}的日线数据，时间范围: {start_date} - {end_date}")
            
            # 使用akshare获取日线数据
            df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                  start_date=start_date, end_date=end_date, adjust="qfq")
            
            if df.empty:
                self.logger.warning(f"股票{code}没有获取到数据")
                return None
            
            # 动态处理列名
            expected_columns = ['trade_date', 'open_price', 'close_price', 'high_price', 'low_price', 
                              'volume', 'amount', 'amplitude', 'pct_change', 'pct_change_amount', 'turnover_rate']
            
            # 检查实际列数
            if len(df.columns) == 11:
                # 11列的情况
                df.columns = expected_columns
            elif len(df.columns) == 12:
                # 12列的情况，可能包含其他字段
                df.columns = expected_columns + ['extra_column']
                df = df.drop('extra_column', axis=1)
            else:
                # 其他情况，只取前11列
                self.logger.warning(f"股票{code}数据列数异常: {len(df.columns)}列，使用前11列")
                df = df.iloc[:, :11]
                df.columns = expected_columns
            
            self.logger.info(f"成功获取股票{code}的{len(df)}条日线数据")
            return df
        except Exception as e:
            self.logger.error(f"获取股票{code}日线数据失败: {e}")
            return None
    
    def calculate_kdj(self, df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """同花顺风格KDJ算法，初始K、D为50，递推"""
        try:
            low_list = df['low_price'].rolling(window=n, min_periods=1).min()
            high_list = df['high_price'].rolling(window=n, min_periods=1).max()
            rsv = (df['close_price'] - low_list) / (high_list - low_list) * 100

            k = [50]
            d = [50]
            for i in range(1, len(df)):
                k.append((2/3) * k[-1] + (1/3) * rsv.iloc[i])
                d.append((2/3) * d[-1] + (1/3) * k[-1])
            df['k_value'] = k
            df['d_value'] = d
            df['j_value'] = 3 * df['k_value'] - 2 * df['d_value']
            return df
        except Exception as e:
            self.logger.error(f"计算KDJ指标失败: {e}")
            return df
    
    def calculate_ma(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算移动平均线"""
        try:
            df['ma5'] = df['close_price'].rolling(window=5).mean()
            df['ma10'] = df['close_price'].rolling(window=10).mean()
            df['ma20'] = df['close_price'].rolling(window=20).mean()
            return df
        except Exception as e:
            self.logger.error(f"计算移动平均线失败: {e}")
            return df
    
    def save_stock_data(self, db: Session, code: str, df: pd.DataFrame) -> bool:
        """保存股票数据到数据库"""
        try:
            for _, row in df.iterrows():
                # 保存日线数据
                daily_data = StockDaily(
                    code=code,
                    trade_date=row['trade_date'],
                    open_price=row['open_price'],
                    high_price=row['high_price'],
                    low_price=row['low_price'],
                    close_price=row['close_price'],
                    volume=row['volume'],
                    amount=row['amount'],
                    turnover_rate=row.get('turnover_rate', 0)
                )
                db.add(daily_data)
                
                # 保存技术指标数据
                if 'k_value' in row and pd.notna(row['k_value']):
                    indicator_data = StockIndicator(
                        code=code,
                        trade_date=row['trade_date'],
                        k_value=row['k_value'],
                        d_value=row['d_value'],
                        j_value=row['j_value'],
                        ma5=row.get('ma5', 0),
                        ma10=row.get('ma10', 0),
                        ma20=row.get('ma20', 0)
                    )
                    db.add(indicator_data)
            
            db.commit()
            return True
        except Exception as e:
            self.logger.error(f"保存股票数据失败: {e}")
            db.rollback()
            return False
    
    def get_latest_data(self, db: Session, code: str) -> Optional[Dict[str, Any]]:
        """获取股票最新数据"""
        try:
            # 获取最新日线数据
            latest_daily = db.query(StockDaily).filter(
                StockDaily.code == code
            ).order_by(StockDaily.trade_date.desc()).first()
            
            # 获取最新技术指标
            latest_indicator = db.query(StockIndicator).filter(
                StockIndicator.code == code
            ).order_by(StockIndicator.trade_date.desc()).first()
            
            if latest_daily and latest_indicator:
                return {
                    'daily': latest_daily,
                    'indicator': latest_indicator
                }
            return None
        except Exception as e:
            self.logger.error(f"获取股票{code}最新数据失败: {e}")
            return None

data_service = DataService() 