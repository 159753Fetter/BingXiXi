from datetime import datetime
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from Test import user, product, shop, manager
from utils.response import standard_response
from utils.times import getMsTime

app = FastAPI()
app.include_router(user.users_router, prefix="/users")
app.include_router(manager.manager_router, prefix="/manager")
app.include_router(shop.shop_router, prefix="/shop")
app.include_router(product.products_router,prefix="/products")
app.include_router(product.index_router,prefix='/homepage')

origins = [
    "*"
]
headers = {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Credentials":"true", "Access-Control-Allow-Methods": "POST,OPTIONS,GET,UPDATE,DELETE"}

@app.exception_handler(HTTPException)  # 自定义HttpRequest 请求异常
async def http_exception_handle(request, exc):
    response = JSONResponse({
        "code": exc.status_code,
        "message": str(exc.detail),
        "data": None,
        "timestamp": getMsTime(datetime.now())
    }, status_code=exc.status_code,headers = headers)
    return response


@app.exception_handler(RequestValidationError)
async def request_validatoion_error(request, exc):
    try:
        message = str(exc.detail)
    except:
        try:
            message = str(exc.raw_errors[0].exc)
        except:
            message = "请求错误"
    response = JSONResponse({
        "code": 400,
        "message": message,
        "data": None,
        "timestamp": getMsTime(datetime.now())
    }, status_code=400,headers = headers)
    return response


@app.exception_handler(Exception)
async def request_validatoion_error(request, exc):
    try:
        message = str(exc)
    except:
        message = None
    response = JSONResponse({
        "code": 500,
        "message": "内部错误",
        "data": message,
        "timestamp": getMsTime(datetime.now())
    }, status_code=500,headers = headers)
    return response


# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的源列表
    allow_credentials=True,  # 允许返回 cookies
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
)

@app.get("/")
@standard_response
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
@standard_response
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


app.mount("/static", StaticFiles(directory="static"), name="static")

def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
