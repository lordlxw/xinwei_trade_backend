#!/usr/bin/env python3
"""
数据初始化脚本
获取一些热门股票的历史数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, init_db
from app.services.data_service import data_service
from loguru import logger

def init_stock_data():
    """初始化股票数据"""
    logger.info("开始初始化股票数据...")
    
    # 初始化数据库
    init_db()
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 获取股票列表
        stock_list = data_service.get_stock_list()
        logger.info(f"获取到 {len(stock_list)} 只股票")
        
        # 选择前10只股票进行数据获取
        test_stocks = stock_list[:10]
        
        for stock in test_stocks:
            code = stock['code']
            name = stock['name']
            
            logger.info(f"正在获取股票 {code} {name} 的数据...")
            
            # 获取日线数据
            df = data_service.get_stock_daily_data(code)
            
            if df is not None and not df.empty:
                # 计算技术指标
                df = data_service.calculate_kdj(df)
                df = data_service.calculate_ma(df)
                
                # 保存到数据库
                success = data_service.save_stock_data(db, code, df)
                if success:
                    logger.info(f"股票 {code} {name} 数据保存成功，共 {len(df)} 条记录")
                else:
                    logger.error(f"股票 {code} {name} 数据保存失败")
            else:
                logger.warning(f"股票 {code} {name} 没有获取到数据")
        
        logger.info("数据初始化完成！")
        
    except Exception as e:
        logger.error(f"数据初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_stock_data() 