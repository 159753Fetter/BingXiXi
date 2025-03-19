import hashlib
from datetime import datetime, date
from typing import Any, Union, Optional

from fastapi import UploadFile, File
from pydantic import BaseModel, ConfigDict, Field

class product_add_interface(BaseModel):
    name: str
    description: str
    price: float
    category: int
    shop_id : int
    stock : int
    image : str

# 可以根据需要添加更多字段，如库存量、商品图片等
class ProductRequest(BaseModel):
    token: str
    id: int

class ProductSearch(BaseModel):
    search_str: str

class ProductBuy(BaseModel):
    product_id: int = 0
    number: int = 0
    user_id: int = 0

class Productcheck(BaseModel):
    product_id: int = 0
    number: int = 0
    user_id: int = 0
    order_id: int = 0

class comment_add(BaseModel):
    product_id: int = 0
    review: str = None
    user_id: int = 0

class add_product(BaseModel):
    image: UploadFile = File(...)
    description: str = Field(..., strip_whitespace=True, min_length=1)
    price: float = Field(..., gt=0)
    name: str = Field(..., strip_whitespace=True, min_length=1)
    shop_id: int = Field(..., gt=0)
    stock: int = Field(..., gt=0)

class detail_interface(BaseModel):
    id: int = 0

class comment_update(BaseModel):
    comment_id : int
    update_review : str

class comment_del(BaseModel):
    comment_id : int

class commnet_search(BaseModel):
    search_str:str

class comment_get(BaseModel):
    product_id : int

class comment_get_all(BaseModel):
    comment_id: int = 0
    review: str = None
    user_id: int = 0
    user_name: str = None
    create_time: datetime = None

class pro_refund(BaseModel):
    order_id: int = 0

class category_interface(BaseModel):
    category: int = 0

class product_interface(BaseModel):
     product_id: int = 0

class dialog_add(BaseModel):
    dialog: str = None
    receive_id: int = 0

class send_interface(BaseModel):
    send_id: int = 0

class dialog_get(BaseModel):
    shop_id: int = 0