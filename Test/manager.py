from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, UploadFile, Form, File
from fastapi import Request, Header, Depends
from Model.db import session_db, user_information_db
from Service.manager import ManagerModel
from Test.user import user_model
from Type.function import get_time_now
from Type.manager import *
from Type.user import login_interface, session_interface, register_interface, user_add_interface, user_edit_interface, \
    order_interface, shop_interface, shop_id_interface
from utils.response import user_standard_response

manager_router = APIRouter()
manager_model = ManagerModel()

# 管理待开业的店铺
@manager_router.post("/shop")
@user_standard_response
async def manager_shop(request: Request):
    headers = request.headers
    Token = headers.get('Authorization')

    shop_list = manager_model.get_all_shop()
    open_shop = []
    close_shop = []
    close_SHOP = []
    for shop in shop_list:
        if shop.status == 0:
            close_shop.append(shop)
        else:
            open_shop.append(shop)

    for item in close_shop:
        shop = shop_interface()
        shop.shop_name = item.name # 商铺名称
        shop.photo = item.picture # 商铺图片
        shop.id = item.id #商铺id
        shop.address = item.address # 商铺地址
        shop.sales_volume = item.sales_volume # 商铺销售额
        shop.time = str(item.creation_time) # 商铺创建时间
        close_SHOP.append(shop.model_dump())
    return {'message': '查看成功', 'data': {"Shop": close_SHOP}, 'code': 0}

# 允许开业的店铺
@manager_router.post("/edit_shop")
@user_standard_response
async def edit_shop_status(request: Request, log_data: edit_shop_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    manager_model.edit_shop(log_data.shop_id)
    return {'message': '修改成功', 'data': False, 'code': 0}

# 不允许开业的店铺
@manager_router.post("/unallow_shop")
@user_standard_response
async def edit_unallow_shop(request: Request, log_data: edit_shop_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    manager_model.edit_unallow_shop(log_data.shop_id)
    return {'message': '修改成功', 'data': False, 'code': 0}

# 查看所有商品
@manager_router.post("/product")
@user_standard_response
async def manager_product(request: Request):
    headers = request.headers
    Token = headers.get('Authorization')

    unallow_product = [] # 待上架商品

    Item = manager_model.get_all_product()
    for item in Item:
        product = product_interface()
        product.product_id = item.id # 商品id
        product.product_name = item.name # 商品名称
        product.price = item.price # 商品价格
        product.product_category = item.category # 商品分类
        product.product_description = item.description # 商品描述
        product.product_picture = item.picture # 商品图片
        product.product_stock = item.stock # 商品库存
        product.shop_id = item.shop_id #所属商铺id
        shop = manager_model.get_shop_by_id(item.shop_id)
        product.shop_name = shop.name
        product.shop_picture = shop.picture
        product.shop_address = shop.address
        if item.status == 0 or item.status == 3:
            unallow_product.append(product.model_dump())
    return {'message': '修改成功', 'data': {"Products": unallow_product}, 'code': 0}

# 允许待通过的商品通过
@manager_router.post("/edit_product")
@user_standard_response
async def edit_product_status(request: Request, log_data: edit_product_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    manager_model.edit_product(log_data.product_id)
    return {'message': '修改成功', 'data': False, 'code': 0}

# 不允许待通过商品通过
@manager_router.post("/unallow_product")
@user_standard_response
async def edit_unallow_product(request: Request, log_data: edit_product_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    manager_model.edit_unallow_product(log_data.product_id)
    return {'message': '修改成功', 'data': False, 'code': 0}

@manager_router.post("/showuser")
@user_standard_response
async def get_under_allow_user(request: Request):
    under_user = {}
    under_user["username"] = []
    Item = user_model.getunderuser()
    for item in Item:
        user = {"user_name" : item.username, "user_id" : item.id}
        under_user["username"].append(user)

    return {
        'message': "返回成功",
        "code": 0,
        "data": under_user
    }

@manager_router.post("/allow_user")
@user_standard_response
async def allow_user(request: Request,under_user : under_user_interface):
    tempid = under_user.user_id
    user_model.update_now_user(tempid)
    return {
        'message' : "修改成功",
        "code" : 0,
        "data" : 1
    }

@manager_router.post("/unallow_user")
@user_standard_response
async def unallow_user(request: Request, under_user : under_user_interface):
    tempid = under_user.user_id
    user_model.ban_now_user(tempid)
    return {
        'message' : "修改成功",
        "code" : 0,
        "data" : 0
    }