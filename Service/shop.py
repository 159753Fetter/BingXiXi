import shutil

from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, join, update, desc
import Model.user
from Model.db import dbSession, dbSessionread
from Model.user import User,Session,Product,Shop
from Type.shop import shop_request, search_shop, shop_updata, add_shop_interface
import datetime


class ShopModel(dbSession, dbSessionread):
    def search_shop(self, keyword):
        """
        根据关键字搜索店铺
        """
        with self.get_db_read() as session:
            shops = session.query(Shop).filter(Shop.name.like(f'%{keyword}%')).all()
            return shops

    def get_shop_info(self, shop_id):
        """
        获取店铺信息
        """
        with self.get_db_read() as session:
            shop = session.query(Shop).filter(Shop.id == shop_id).first()
            return shop

    def update_shop(self,obj:shop_updata):
        with self.get_db() as session:
            session.query(Product).filter(Product.id == id).update(obj)
            session.commit()
            return id

    def delete_shop(self, id: int):  # 删除商品
            with self.get_db() as session:
                shop = session.query(Shop).filter(Shop.id == id).first()
                if shop is None:
                    # 如果没有找到商品，则返回None
                    return None
                # 删除商品
                session.delete(shop)
                session.commit()
                return id

    def add_shop(self, obj: add_shop_interface):
        obj_dict = jsonable_encoder(obj)
        with self.get_db_read() as session:
            item = session.query(Shop).filter(Shop.user_id == obj_dict.get('user_id'), Shop.name == obj_dict.get('name')).first()
            session.commit()
        if item is None:
            shop_add = Shop(name=obj_dict.get('name'), user_id=obj_dict.get('user_id'), creation_time=datetime.datetime.now(),
                        sales_volume=0, picture = obj_dict.get('photo') ,address=obj_dict.get('address'), status = 0)
            with self.get_db() as session:
                session.add(shop_add)
                session.commit()
                return shop_add.id
        else:
            return item.name

    def close_shop(self, shop_id: int):
        with self.get_db_read() as session:
            session.query(Shop).filter(Shop.id == shop_id).update({"status": 3})
            session.commit()

        with self.get_db() as session:
            session.query(Product).filter(Product.shop_id == shop_id).update({"status": 3})
            session.commit()

    def reapply_shop(self, shop_id: int):
        with self.get_db_read() as session:
            session.query(Shop).filter(Shop.id == shop_id).update({"status": 0})
            session.commit()

        with self.get_db() as session:
            session.query(Product).filter(Product.shop_id == shop_id).update({"status": 0})
            session.commit()