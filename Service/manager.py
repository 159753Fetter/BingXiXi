import shutil

from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, join, update, desc
import Model.user
from Model.db import dbSession, dbSessionread
from Model.user import User, Session, Order, Product, Shop
from Type.user import session_interface, user_add_interface, user_edit_interface

class ManagerModel(dbSession, dbSessionread):
    def get_all_shop(self):  # 管理员获取所有的店铺
        with self.get_db_read() as session:
            shop = session.query(Shop).all()
            session.commit()
            return shop

    def edit_shop(self, shop_id: int): # 修改店铺状态允许开店
        with self.get_db_read() as session:
            shop = session.query(Shop).filter(Shop.id == shop_id).update({"status": 1})
            session.commit()
            return shop

    def edit_unallow_shop(self, shop_id: int): # 修改店铺状态不允许开店
        with self.get_db_read() as session:
            shop = session.query(Shop).filter(Shop.id == shop_id).update({"status": 2})
            session.commit()
            return shop

    def get_all_product(self): # 管理员获取所有的商品
        with self.get_db_read() as session:
            product = session.query(Product).all()
            session.commit()
            return product

    def get_shop_by_id(self, shop_id: int):  # 修改商品状态允许售卖
        with self.get_db_read() as session:
            shop = session.query(Shop).filter(Shop.id == shop_id).first()
            session.commit()
            return shop

    def edit_product(self, product_id: int): # 修改商品状态允许售卖
        with self.get_db_read() as session:
            session.query(Product).filter(Product.id == product_id).update({"status": 1})
            session.commit()

    def edit_unallow_product(self, product_id: int): # 修改商品状态不允许售卖
        with self.get_db_read() as session:
            session.query(Product).filter(Product.id == product_id).update({"status": 2})
            session.commit()