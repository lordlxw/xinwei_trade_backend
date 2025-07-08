from fastapi.responses import JSONResponse
from app.models.response import APIResponse

def api_response(value=None, message="success", code="00000"):
    return JSONResponse(
        status_code=200,
        content=APIResponse(message=message, code=code, value=value).dict()
    ) 