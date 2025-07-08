from fastapi import APIRouter
from app.api.endpoints import stock

api_router = APIRouter()

# 注册股票相关路由
api_router.include_router(
    stock.router,
    prefix="/stock",
    tags=["股票"]
) 