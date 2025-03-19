import datetime
import json
import random
import string
import time
import os
import uuid
from hashlib import scrypt

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, UploadFile, Form, File, Query
from fastapi import Request, Header, Depends
from Model.db import session_db, user_information_db
from Service.user import UserModel, SessionModel
from Type.function import get_time_now
from Type.user import login_interface, session_interface, register_interface, user_add_interface, user_edit_interface, \
    order_interface, shop_interface, shop_id_interface, card_interface, unproduct_interface, user_shop_interface, \
    product_id_interface, edit_address_interface, order_confirmation_interface
from utils.response import user_standard_response

users_router = APIRouter()
user_model = UserModel()
session_model = SessionModel()

# 输入账号密码进行登录
@users_router.post("/login")
@user_standard_response
async def user_login(log_data: login_interface, request: Request, user_agent: str = Header(None)):
    Type = log_data.type # 获取类型
    user_information = user_model.get_user_by_usernametype(log_data.username, log_data.type)
    if user_information is None: # 为空说明用户名不存在
        return {'message': '用户名或密码不正确', 'data': False, 'code': 1}
    else:   # 用户名存在
        new_password = log_data.password

        msg_bytes = new_password.encode("utf8")
        salt = "477d15cb740ca1da08f6d851361b3c80"
        salt_bytes = salt.encode("utf8")
        n, r, p = 4, 8, 16
        hmac = scrypt(msg_bytes, salt=salt_bytes, n=n, r=r, p=p)
        HashPassword = hmac.hex()

        if HashPassword == user_information.password:
            token = str(uuid.uuid4().hex)
            session = session_interface(user_id=int(user_information.id), ip=request.client.host,
                                        func_type=0,
                                        token=token, user_agent=user_agent, exp_dt=
                                        get_time_now('days', 14))
            session_model.add_session(session)
            if log_data.username == "admin":
                Type = 2
            return {'message': '登陆成功', 'data': {"token": token, "type": Type}, 'code': 0}
        else:
            return {'message': '用户名或密码不正确', 'data': False, 'code': 1}

# 输入账号密码进行注册
@users_router.post("/register")
@user_standard_response
async def user_register(log_data: register_interface):
    user_information = user_model.get_user_by_username(log_data.username)
    if user_information is not None: # 不为空说明用户名已经存在
        return {'message': '该用户名已经被注册过', 'data': False, 'code': 1}
    else:   # 为空说明用户名不存在
        Username = log_data.username
        Password = log_data.password
        preference_list = log_data.category_id
        Preference = 0
        for item in preference_list:
            Preference += pow(2, item)
        Type = log_data.type
        Id = user_model.get_count() + 1
        Has_delete = 0

        msg_bytes = Password.encode("utf8")
        salt = "477d15cb740ca1da08f6d851361b3c80"
        salt_bytes = salt.encode("utf8")
        n, r, p = 4, 8, 16
        hmac = scrypt(msg_bytes, salt=salt_bytes, n=n, r=r, p=p)
        HashPassword = hmac.hex()

        user = user_add_interface()
        user.username = Username
        user.password = HashPassword
        if Type == 0:
            user.type = 4
        if Type == 1:
            user.type = 5
        user.id = Id
        user.has_delete = Has_delete
        user.preference = Preference
        user_model.add_user(user)
        return {'message': '注册成功', 'data':False, 'code': 0}

# 进行个人信息修改（商家用户通用）
@users_router.post("/edit")
@user_standard_response
async def user_edit(request: Request, address: str = Form(None), phone: str = Form(None),
                    id_card_number: str = Form(None), photo: UploadFile = File(None)):
    headers = request.headers
    Token = headers.get('Authorization')
    Phone = phone
    Address = address
    Id_card_number = id_card_number
    Photo = photo

    if Phone is not None:
        valid_phone = user_model.get_user_by_phone(Phone, Token) # 判断用户修改后的手机号是否被其他用户使用
        if valid_phone is not None: # 不为空说明手机号已经存在
            return {'message': '该手机号已经被使用，请重新输入', 'data': False, 'code': 1}

    if Id_card_number is not None:
        valid_id = user_model.get_user_by_id(Id_card_number, Token) # 判断用户修改后的身份证号是否被其他用户使用
        if valid_id is not None: # 不为空说明身份证号已经存在
            return {'message': '该身份证号已经被使用，请重新输入', 'data': False, 'code': 1}

    path = "F:\\fastApiProject\static\\user_photo"  # 文件夹路径
    count = 0
    for file in os.listdir(path):  # file 表示的是文件名
        count = count + 1
    count = count + 1
    user = user_edit_interface()
    if Photo is not None:
        user.photo = "/static/user_photo/" + str(count) + ".jpg"
        if Photo.content_type.startswith('application'):
            user_model.save_upload_file(Photo, f"F:\\fastApiProject\static\\user_photo/{count}.jpg") # 保存文件到指定位置
    user.address = Address
    user.phone = Phone
    user.id_card_number = Id_card_number
    user.token = Token
    user_model.edit_user(user)
    User = user_model.get_user_by_token(Token)
    return {'message': '修改成功', 'data': {"phone": User.phone_number, "id_card_number": User.id_card_number,
     "address": User.address, "photo": User.photo}, 'code': 0}

# 查看个人信息（商家用户通用）
@users_router.post("/information")
@user_standard_response
async def user_information(request: Request):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)

    return {'message': '查看成功', 'data': {"phone": User.phone_number,  "id_card_number": User.id_card_number,
       "address": User.address, "photo": User.photo}, 'code': 0}

# 用户查看个人订单（自己的订单）
@users_router.post("/order")
@user_standard_response
async def user_order(request: Request):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    Product = []
    Order = user_model.get_order_by_id(User.id)

    for order in Order:
        if order.status != 0 :
            product = order_interface()
            id = order.product_id
            product_shop = user_model.get_product_shop(id)
            shop = user_model.get_shop_name(product_shop.shop_id)

            product.name = product_shop.name  # 商品名字
            product.shop_id = product_shop.shop_id # 店铺id
            product.photo = product_shop.picture  # 商品照片
            product.address = order.address  # 商品到达地址
            product.quantity = order.quantity  # 商品数量
            product.amount = order.amount  # 商品价钱
            product.status = order.status  # 商品状态
            product.shop_name = shop.name  # 商品所在店铺名
            product.order_id = order.id # 该订单的订单号
            product.product_id = order.product_id # 商品id
            product.time = str(order.create_dt) # 该订单的创建时间

            product = product.model_dump() # 将自定义类型转化为json类型数据
            Product.append(product)
    return {'message': '查看成功', 'data': {"Product": Product}, 'code': 0}

# 商家查看个人店铺以及店铺订单
@users_router.post("/shop")
@user_standard_response
async def user_shop(request: Request):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    SHOP = []
    Shop = user_model.get_shop_by_id(User.id)
    for item in Shop:
        if item.status != 1:
            continue
        shop = shop_interface()
        shop.shop_name = item.name # 商铺名称
        shop.id = item.id #商铺id
        shop.photo = item.picture # 商铺图片
        shop.address = item.address # 商铺地址
        shop.sales_volume = item.sales_volume # 商铺销售额
        shop.time = str(item.creation_time) # 商铺创建时间

        order_list = user_model.get_order_by_shop_id(item.id) # 获取该商铺中所有订单

        for order in order_list:
            product = order_interface()
            product_infor = user_model.get_product_by_product_id(order.product_id) # 根据商品id获取商品信息
            product.name = product_infor.name  # 商品名字
            product.shop_id = item.id  # 店铺id
            product.photo = product_infor.picture  # 商品照片
            product.address = order.address  # 商品到达地址
            product.quantity = order.quantity  # 商品数量
            product.shop_name = item.name # 商铺名称
            product.amount = order.amount  # 商品价钱
            product.status = order.status  # 商品状态
            product.order_id = order.id  # 该订单的订单号
            product.product_id = order.product_id  # 商品id
            product.time = str(order.create_dt)  # 该订单的创建时间
            if order.status != 0:
                shop.order.append(product.model_dump())
        SHOP.append(shop.model_dump())
    return {'message': '查看成功', 'data': {"SHOP": SHOP}, 'code': 0}

# 个人确定收货
@users_router.post("/goods")
@user_standard_response
async def user_goods(request: Request, log_data: shop_id_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    Order = user_model.get_order_by_order_id(log_data.id)
    if(Order.status == 3):
        return {'message': '订单已确认', 'data': False, 'code': 1}
    User = user_model.get_user_by_token(Token)
    id = User.id
    order_id = log_data.id
    user_model.edit_order(id, order_id)
    return {'message': '确认成功','data':False, 'code': 0}

# 个人查看购物车
@users_router.post("/cart")
@user_standard_response
async def user_goods(request: Request):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    Order = user_model.get_order_by_id(User.id)
    Order_list = []
    for order in Order:
        if order.status == 0:
            product = order_interface()
            product_infor = user_model.get_product_by_product_id(order.product_id) # 根据商品id获取商品信息
            shop = user_model.get_shop_name(product_infor.shop_id)
            product.name = product_infor.name  # 商品名字
            product.shop_id = shop.id  # 店铺id
            product.photo = product_infor.picture  # 商品照片
            product.address = order.address  # 商品到达地址
            product.quantity = order.quantity  # 商品数量
            product.shop_name = shop.name # 商铺名称
            product.amount = order.amount  # 商品价钱
            product.product_id = order.product_id  # 商品id
            product.order_id = order.id #订单id
            product.time = str(order.create_dt)  # 该订单的创建时间
            Order_list.append(product.model_dump())

    return {'message': '查看成功', 'data': {"Order": Order_list}, 'code': 0}

# 商家查看待审核店铺
@users_router.post("/audit_shop")
@user_standard_response
async def user_close_shop(request: Request):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    close_shop = user_model.get_check_shop(User.id)
    Audit_shop = []
    Close_shop = []
    Reapply_shop = []

    for item in close_shop:
        shop = shop_interface()
        shop.shop_name = item.name  # 商铺名称
        shop.id = item.id  # 商铺id
        shop.photo = item.picture  # 商铺图片
        shop.address = item.address  # 商铺地址
        shop.sales_volume = int(item.sales_volume)  # 商铺销售额
        shop.time = str(item.creation_time)  # 商铺创建时间
        if item.status == 0:
            Audit_shop.append(shop.model_dump())
        if item.status == 2:
            Close_shop.append(shop.model_dump())
        if item.status == 3:
            Reapply_shop.append(shop.model_dump())

    return {'message': '返回成功', 'data': {"Audit_shop": Audit_shop, "Close_Shop": Close_shop, "Reapply_shop": Reapply_shop}, 'code': 0}

# 用户删除购物车中商品
@users_router.post("/delete_card")
@user_standard_response
async def user_delete_card(request: Request, log_data: card_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    user_model.delete_order_by_id(User.id, log_data.id)
    return {'message': '删除成功', 'data': False, 'code': 0}

# 商家查看待通过商品
@users_router.post("/look_product")
@user_standard_response
async def user_look_product(request: Request, log_data: shop_id_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    unproducts = user_model.look_unproduct(log_data.id)
    Product = []
    for item in unproducts:
        product = unproduct_interface()
        product.name = item.name
        product.description = item.description
        product.price = item.price
        product.id = item.id
        product.stock = item.stock
        product.photo = item.picture
        product.category_id = item.category
        Product.append(product.model_dump())
    return {'message': '查看成功',  'data': {"Products": Product}, 'code': 0}

# 商家查看未通过商品
@users_router.post("/look_unproduct")
@user_standard_response
async def user_look_unproduct(request: Request, log_data: shop_id_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    unproduct = user_model.look_unproducts(log_data.id)
    Product = []
    for item in unproduct:
        product = unproduct_interface()
        product.name = item.name
        product.description = item.description
        product.price = item.price
        product.category_id = item.category
        product.id = item.id
        product.stock = item.stock
        product.photo = item.picture
        Product.append(product.model_dump())
    return {'message': '查看成功',  'data': {"Products": Product}, 'code': 0}

# 商家删除未通过商品
@users_router.post("/delete_unproduct")
@user_standard_response
async def user_delete_unproduct(request: Request, log_data: product_id_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    user_model.delete_product_by_id(log_data.id)
    return {'message': '删除成功', 'data': False, 'code': 0}

# 商家修改订单物流信息
@users_router.post("/edit_address")
@user_standard_response
async def user_delete_unproduct(request: Request, log_data: edit_address_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    user_model.edit_address(log_data.order_id, log_data.address)
    return {'message': '修改成功', 'data': False, 'code': 0}

# 商家确认发货
@users_router.post("/confirmation")
@user_standard_response
async def user_confirmation(request: Request, log_data: order_confirmation_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    user_model.confirm_order(log_data.order_id)
    return {'message': '确认成功', 'data': False, 'code': 0}

# 用户查看商家店铺
@users_router.post("/look_shop")
@user_standard_response
async def user_look_shop(request: Request, log_data: shop_id_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    item = user_model.get_shop_name(log_data.id)
    shop = user_shop_interface()
    shop.shop_name = item.name # 商店名称
    shop.photo = item.picture # 商铺头像
    shop.sales_volume = item.sales_volume # 商铺销售额
    shop.address = item.address # 商店地址
    shop.time = str(item.creation_time)  # 商铺开店时间
    shop = shop.model_dump()
    Product = user_model.get_all_products(log_data.id)
    Products = [
        {"id": product.id, "name": product.name, "url": product.picture, "price": str(product.price)}
        for product in Product]

    return {'message': '查看成功',  'data': {'Shop': shop, 'Product': Products}, 'code': 0}

'''
# 下线
@users_router.put("/logout") 
@user_standard_response
async def user_logout(request: Request):
    token = session['token']
    mes = session_model.delete_session_by_token(token)  # 将session标记为已失效
    session_db.delete(token)  # 在缓存中删除
    return {'message': '下线成功', 'data': {'result': mes}, 'token': '-1', 'code': 0}
'''