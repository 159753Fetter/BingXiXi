from Model.user import Product
from Type.product import ProductBuy, Productcheck
from utils.response import product_response,user_standard_response,standard_response
from fastapi import APIRouter, HTTPException, FastAPI, UploadFile, File
from Service.product import ProductModel
from Service.user import UserModel, SessionModel
from Type.shop import shop_request, search_shop, shop_updata, add_shop_interface, order_interface, shop_interface
from Service.shop import ShopModel
from Service.product import ProductModel
import datetime
import os
from fastapi.encoders import jsonable_encoder
from fastapi import Request, Header, Depends,Form

shop_router = APIRouter()
shopmodel= ShopModel()
user_model = UserModel()
product_model = ProductModel()

@shop_router.post("/detail")
@standard_response
async def get_shop(request: Request, shop_id: int = 0):
    headers = request.headers
    Token = headers.get('Authorization')
    temp_shop = shopmodel.get_shop_info(shop_id)
    if temp_shop == None:
        return {
            "code": 1
        }
    owner_name = user_model.get_user_by_id(temp_shop.user_id, Token)
    products = product_model.get_products_shop(shop_request.id)
    return{
            "code": 0,
            "Shopname": temp_shop.name,
            "owner_id": temp_shop.user_id,
            "owner_name": owner_name,
            "create_time": temp_shop.creation_time,
            "sales_volume": temp_shop.sales_volume,
            "products": products
    }

@shop_router.post("/search")
@standard_response
async def search_shop(request: Request,request_data:search_shop):
    shops = shopmodel.search_shop(request_data.temp)
    shop_searched = [
        {
            "code": 0,
            "Shopname": shop.name,
            "owner_id": shop.user_id,
            "owner_name": shopmodel.get_shop_info(shop.id),
            "create_time": shop.creation_time,
            "sales_volume": shop.sales_volume,
    }
    for shop in shops
    ]
    return{
        'data' : shop_searched
    }

@shop_router.post("/detail")
@standard_response
async def update_shop(request: Request,up_data : shop_updata):
    headers = up_data.header()
    Token = headers.get("Authorization")
    up_data.user_id = user_model.get_user_by_token(Token)
    temp = shopmodel.update_shop(up_data)
    if(temp == None) :
        return {
            'error'
        }

@shop_router.post("/add")
@standard_response
async def add_shop(request: Request, shop_name: str = Form(None),
                    address: str = Form(None), Photo: UploadFile = File(None)):

    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)

    shop = add_shop_interface()
    shop.user_id = User.id # 商家id
    shop.address = address # 店铺地址
    shop.name = shop_name # 店铺名字

    path = "F:\\fastApiProject\static\\shop_photo"  # 文件夹路径
    count = 0
    for file in os.listdir(path):  # file 表示的是文件名
        count = count + 1
    count = count + 1

    if Photo.content_type.startswith('application'):
        user_model.save_upload_file(Photo, f"F:\\fastApiProject\static\shop_photo/{count}.jpg")  # 保存文件到指定位置
    shop.photo = "/static/shop_photo/" + str(count) + ".jpg" # 店铺头像

    item = shopmodel.add_shop(shop)
    if item == shop_name:
        return {'message': '创建失败', 'data': False, 'code': 1}
    else:
        return {'message': '创建成功', 'data': True, 'code': 0}

@shop_router.delete("/detail")
@standard_response
async def delete_product(product_id: int ):
    temp = shopmodel.delete_shop(product_id)
    if temp == None:
        return {
            "message": '此商品不存在',
            "code": 1
        }
    else:
        return {
            'message': '删除成功',
            "code": 0
        }

@shop_router.post("/order")
@standard_response
async def delete_order(request: Request, log_data: order_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    Order_list = []
    for it in log_data:
        Order_list = it[1]
    for item in Order_list:
        user_model.delete_order_by_id(User.id, item)
    return 'success'

@shop_router.post("/checkout")
@user_standard_response
async def checkout_order(request: Request, log_data: order_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    Order_list = []
    for it in log_data:
        Order_list = it[1]
    for item in Order_list:
        buy_product = Productcheck()
        Order = user_model.get_order_by_order_id(item)
        buy_product.user_id = User.id
        buy_product.product_id = Order.product_id
        buy_product.order_id = Order.id
        buy_product.number = Order.quantity
        tt = product_model.purchase_product3(buy_product)
        if tt == 0:
            return {'message': 'Product not found', 'data': False, 'code': 1}
        if tt == 1:
            return {'message': 'Not enough stock available', 'data': False, 'code': 1}
    return {"message": 'success', 'data': False, 'code': 0}

@shop_router.post("/shop_close")
@user_standard_response
async def shop_close(request: Request, log_data: shop_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    shopmodel.close_shop(log_data.shop_id)
    return {"message":'success', 'data':True, 'code': 0}

@shop_router.post("/shop_reapply")
@user_standard_response
async def shop_reapply(request: Request, log_data: shop_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    shopmodel.reapply_shop(log_data.shop_id)
    return {"message":'success', 'data': True, 'code': 0}