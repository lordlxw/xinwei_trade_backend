from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

from app.services.data_service import data_service
from app.core.config import settings

class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=settings.SCHEDULER_TIMEZONE)
        self.logger = logger
    
    def start(self):
        """启动调度器"""
        try:
            # 启动调度器
            self.scheduler.start()
            self.logger.info("定时任务调度器启动成功")
        except Exception as e:
            self.logger.error(f"启动定时任务调度器失败: {e}")
    
    def stop(self):
        """停止调度器"""
        try:
            self.scheduler.shutdown()
            self.logger.info("定时任务调度器已停止")
        except Exception as e:
            self.logger.error(f"停止定时任务调度器失败: {e}")
    

    
    def get_job_status(self):
        """获取任务状态"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            })
        return jobs

# 创建全局调度器实例
task_scheduler = TaskScheduler() 