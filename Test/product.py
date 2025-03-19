import json
import random
from time import sleep
from urllib.parse import urljoin

import requests
from fastapi.responses import FileResponse
from fastapi import Request, Form

from Model.user import Product
from Type.shop import pro_update
from utils.response import product_response, user_standard_response, standard_response
from fastapi import APIRouter, HTTPException, FastAPI, UploadFile, File, Query
from Service.product import ProductModel
from Type.product import product_add_interface, ProductRequest, ProductSearch, detail_interface, comment_add, \
    commnet_search, comment_get, comment_get_all, comment_del, pro_refund, category_interface, product_interface, \
    dialog_add, send_interface, dialog_get
from Service.user import UserModel, SessionModel
from Type.product import product_add_interface,ProductRequest,ProductSearch,ProductBuy
from Service.user import UserModel, SessionModel
from Service.shop import ShopModel

products_router = APIRouter()
index_router = APIRouter()
user_model = UserModel()
product_model = ProductModel()
session_model = SessionModel()
shopmodel = ShopModel()


@products_router.post("/details")
@standard_response
async def get_product(request: Request, log_data: detail_interface):
    Product = product_model.get_product_by_id(log_data.id)
    if (Product.status == 0):
        return {"code": 1}
    elif (Product == None):
        return {"code": 1}
    else:
        return {
                "code": 1,
                "image": Product.picture,
                "description": Product.description,
                "price": Product.price,
                "name" : Product.name,
                "category_id": Product.category,
                "status": Product.status,
                "shop" :{
                    "id" : Product.shop_id,
                    "name" : shopmodel.get_shop_info(Product.shop_id).name,
                    "address" : shopmodel.get_shop_info(Product.shop_id).address
                }
        }

@products_router.post("/add")
@standard_response
async def add_product(request: Request, product: product_add_interface):
    if product_model.add_product(product) == 'e':
        return {
            "code": 0
        }
    else:
        return {
            "code": 1
        }

@products_router.post("/detail")
@standard_response
async def add_product(request: Request,product: product_add_interface):
    if product_model.add_product(product) == 'e':
        return {
            "code": 0
        }
    else:
        return {
            "code": 1
        }

@products_router.post("/detail/change")
@standard_response
async def update_product(request: Request, product_id: int = Form(None), price: float = Form(None),
                         name: str = Form(None), description: str = Form(None), shop_id: int = Form(None),
                         stock: int = Form(None), image: UploadFile = File(None), category_id: int = Form(None)):
    update_data = pro_update()
    update_data.product_id = product_id
    update_data.price = price
    update_data.name = name
    update_data.description = description
    update_data.shop_id = shop_id
    update_data.stock = stock
    update_data.image = image
    update_data.category = category_id
    print(category_id)
    t = product_model.update_pro(update_data)
    return{"code": 1}

@products_router.post("/detail/del")
@standard_response
async def delete_product(request: Request,tt:  comment_del):
    aa = product_model.delete_product(tt)
    if aa == 1:
        return{"code": 1}
    else:
        return {"code": 0}

@index_router.get("/")
@standard_response
async def get_homepage(request: Request):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    prefrence_list = []

    temp = bin(User.preference).replace('0b','')
    i = len(temp)
    for it in temp:
        i = i - 1
        if it == '1':
            prefrence_list.append(i)
    recommendation_list = []
    cnt = 0
    while cnt < 3:
        t = random.randint(1, 16)
        if t not in prefrence_list:
            cnt += 1
            prefrence_list.append(t)

    for it in prefrence_list:
        recommendations = product_model.get_products(it)
        for item in recommendations:
            recommendation_list.append(item)

    random.shuffle(recommendation_list)
    recommendation =[
        {"id": product.id, "name": product.name, "url": product.picture, "price": str(product.price)}
        for product in recommendation_list
    ]

    big_picture_data = product_model.get_bigpicture_product()
    big_picture = [
        {"id": product.id, "name": product.name, "url": "/static/bigpicture/" + str(product.id) + ".png", "price": str(product.price)}
        for product in big_picture_data
    ]

    return {'big_pictures': big_picture,
            'recommends': recommendation,
            "code": 0
    }

@products_router.post("/search")
@standard_response
async def search_product(search_pro: ProductSearch):
    products = product_model.get_products_by_name(search_pro.search_str)
    if products == None:
        return {
            "code": 1
        }
    else:
        temp = [
            {"product_id": product.id, "productname": product.name, "price":product.price, "url": product.picture}
            for product in products
        ]
        return temp

@products_router.post("/test_img")
@standard_response
async def upload_file(file: UploadFile = File(...)):
    db = ProductModel()
    try:
        # 检查文件类型
        if file.content_type.startswith('image'):
            # 保存文件到指定位置
            db.save_upload_file(file, f"uploaded_files/{file.filename}")
            return 1
        else:
            return 2
    except Exception as e:
        return str(e)

@products_router.post("/detail")
@standard_response
async def but_pro(buy_pro: ProductBuy):
    tt = ProductModel.purchase_product(ProductBuy)
    if tt == 'e':
        return {
            "code": 1
        }
    else:
        return {
            "code": 0
        }

@products_router.get("/acquire_img")
async def acquire_image(path: str = Query()):
    # 从文件系统中读取图片内容
    return FileResponse(path, media_type="image/png")

@products_router.post("/get_all_products_from_shop")
@standard_response
async def get_all_products_from_shop(request: Request, log_data: detail_interface):
    db = ProductModel()
    return db.search_all_products(log_data.id)

@products_router.post("/shopkeeper_add_product")
@standard_response
async def shopkeeper_add_product(request: Request, description: str = Form(None),
                                 price: float = Form(None),
                                 name: str = Form(None),
                                 shop_id: int = Form(None),
                                 stock: int = Form(None),
                                 image: UploadFile = File(None),
                                 category_id: int = Form(None)):
    db = ProductModel()
    return db.shopkeeper_add_product(description, price, name, shop_id, stock, image,category_id)

@products_router.post("/detail/comment")
@user_standard_response
async def comment_add(request: Request,temp_comment: comment_add):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    temp_comment.user_id = User.id
    url = "http://23.95.222.103:8080/wordscheck"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "content": temp_comment.review
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    sleep(1)
    temp_comment.review = response.json()["return_str"]
    aa = product_model.add_comment(temp_comment)
    if aa == 'error':
        return {"message": '尚未购买，无法评论', 'data': False, "code": 1}
    else:
        return {"message": 'success', 'data': False, "code": 0}

@products_router.post("/detail/buy1")
@user_standard_response
async def buy_product1(request: Request, buy_pro: ProductBuy):   # 商品直接购买
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    buy_pro.user_id = User.id

    category = product_model.get_category_of_product(buy_pro.product_id)
    preference = bin(User.preference).replace('0b', '').zfill(17)
    preference = preference[:-1]
    modified_preference = product_model.change_preference(preference=preference[::-1])
    string_list = list(modified_preference)
    string_list[category - 1] = '1'
    new_string = ''.join(string_list)
    new_preference = 0
    cnt = 1
    for item in new_string:
        if item == '1':
            new_preference += pow(2, cnt)
        cnt = cnt + 1
    user_model.save_preference(user_id=buy_pro.user_id, preference=new_preference)

    tt = product_model.purchase_product1(buy_pro)
    if tt == "e":
        return {"message": 'error', 'data': False, "code": 0}
    else:
        if tt == 0:
            return {'message': 'Product not found', 'data': False, 'code': 1}
        if tt == 1:
            return {'message': 'Not enough stock available', 'data': False, 'code': 1}
        if tt == 2:
            return {"message": 'success', 'data': True, "code": 0}

@products_router.post("/detail/buy2")
@standard_response
async def buy_product2(request: Request, buy_pro: ProductBuy):   # 商品添加至购物车
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)

    category = product_model.get_category_of_product(buy_pro.product_id)
    preference = bin(User.preference).replace('0b', '').zfill(17)
    preference = preference[:-1]
    modified_preference = product_model.change_preference(preference=preference[::-1])
    string_list = list(modified_preference)
    string_list[category - 1] = '1'
    new_string = ''.join(string_list)
    new_preference = 0
    cnt = 1
    for item in new_string:
        if item == '1':
            new_preference += pow(2, cnt)
        cnt = cnt + 1
    user_model.save_preference(user_id=buy_pro.user_id, preference=new_preference)

    buy_pro.user_id = User.id
    tt = product_model.purchase_product2(buy_pro)
    if tt == "e":
        return 'error'
    else:
        return 'success'

@products_router.post("/search/category")
@standard_response
async def search_product_by_category(request: Request, category: category_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    products = product_model.get_products(category=category.category, limit=30)
    temp = [
        {"product_id": product.id, "productname": product.name, "price": product.price, "url": product.picture}
        for product in products
    ]
    return temp

@products_router.get("/detail/buy") #用户购买页面信息接口
@standard_response
async def getuserbuyinfo(request: Request):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    return{
        "address": User.address,
        "phone_number": User.phone_number
    }

@products_router.post("/detail/comment/search")
@standard_response
async def search_comment(request: Request, tempsearch: commnet_search):
    cc = product_model.search_comment(tempsearch.search_str)
    if cc == None:
        return 'error'
    ttc = [
        {"comment_id": comment.id, "review": comment.review, "user_id": comment.user_id,
         "user_name": user_model.get_username_by_id(comment.user_id)}
        for comment in cc
    ]
    return ttc

@products_router.post("/detail/comment/view")
@standard_response
async def get_comment(request:Request , get_comment: comment_get):
    headers = request.headers
    Token = headers.get('Authorization')
    cc = product_model.get_comment(get_comment.product_id)
    ttc = []
    for comment in cc:
        c = comment_get_all()
        c.comment_id = comment.id
        c.review = comment.review
        c.user_id = comment.user_id
        c.user_name = user_model.get_user_by_token(Token).username
        c.create_time = str(comment.create_dt)
        ttc.append(c.model_dump())
    return ttc

@products_router.post("/detail/refund")
@user_standard_response
async def refund(request: Request, log_data: pro_refund):
    headers = request.headers
    Token = headers.get('Authorization')
    temp_order = product_model.get_status_f_orderid(log_data.order_id)
    if(temp_order.status == 4):
        return {'message': '商品已退款，无法退款','data': False, 'code': 1}
    product_model.refund_deal(temp_order.product_id, temp_order.quantity, temp_order.amount, log_data.order_id)
    return {'message': 'success','data': False, 'code': 0}

@products_router.post("/sell_out") # 商品下架
@standard_response
async def sell_out(request: Request, log_data: product_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    product_model.sell_out(log_data.product_id)
    return 'success'

@products_router.post("/reapply") # 商品重新提交
@standard_response
async def reapply(request: Request, log_data: product_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    product_model.reapply(log_data.product_id)
    return 'success'

@products_router.post("/dialog")
@standard_response
async def dialog(request: Request, log_data: dialog_add):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    if User.identity_type == 0:
        receive_id = product_model.get_shop_user_id(log_data.receive_id)
        product_model.add_dialog(send_id=User.id, receive_id=receive_id, dialog=log_data.dialog)
    else:
        product_model.add_dialog(send_id=User.id, receive_id=log_data.receive_id, dialog=log_data.dialog)
    return 'success'

@products_router.post("/get_dialog")
@standard_response
async def get_dialog(request: Request, log_data: send_interface):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    if User.identity_type == 1:
        result = product_model.get_dialog(log_data.send_id, User.id)
    else:
        Send_id = product_model.get_shop_user_id(log_data.send_id)
        result = product_model.get_dialog(Send_id, User.id)
    return result

@products_router.post("/get_shop_dialog")
@standard_response
async def dialog(request: Request, log_data: dialog_get):
    headers = request.headers
    Token = headers.get('Authorization')
    User = user_model.get_user_by_token(Token)
    receive_ids = product_model.get_shop_dialog_user_id(log_data.shop_id)
    return receive_ids