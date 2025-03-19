import hashlib
from datetime import datetime, date
from typing import Any, Union, Literal, Optional

from fastapi import UploadFile, File, Form
from pydantic import BaseModel, ConfigDict, Field

class product_interface(BaseModel): # 管理员管理商品使用
    product_id: int = 0
    product_name: str = None
    product_category: str = None
    price: float = 0.0
    product_picture: str = None
    product_description: str = None
    product_stock: int = 0
    shop_id: int = 0
    shop_name: str = None
    shop_picture: str = None
    shop_address: str = None

class edit_product_interface(BaseModel): #管理员允许商品上架
    product_id: int = 0

class edit_shop_interface(BaseModel):  # 管理员允许商家开业
    shop_id: int = 0

class under_allow_user(BaseModel):
    user_id: int = 0

class under_user_interface(BaseModel):
    user_id: int = 0