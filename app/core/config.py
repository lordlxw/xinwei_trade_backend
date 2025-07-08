from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AI量化系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./quant_system.db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # 数据源配置
    TUSHARE_TOKEN: Optional[str] = os.getenv("TUSHARE_TOKEN")
    
    # 定时任务配置
    SCHEDULER_TIMEZONE: str = "Asia/Shanghai"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/quant_system.log"
    

    
    class Config:
        env_file = ".env"

settings = Settings() 