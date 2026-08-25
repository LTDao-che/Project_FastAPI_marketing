from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
from app.schemas.response import BaseResponse

def error_response(req: Request, status_code: int, message: str, data = None, errors = None):
    body = BaseResponse(
        status_code= status_code,
        message= message,
        data = data,
        errors = errors,
        timestamp= datetime.now().isoformat(),
        path = req.url.path
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump()
    )

def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(
        req=request,
        status_code=exc.status_code,
        message=exc.detail
    )

def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        req=request,
        status_code=422,
        message="Dữ liệu đầu vào không hợp lệ",
        errors=exc.errors()
    )

def generic_exception_handler(request: Request, exc: Exception):
    return error_response(
        req=request,
        status_code=500,
        message="Lỗi hệ thống, vui lòng thử lại sau"
    )