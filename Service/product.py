import shutil
from urllib.parse import urljoin

from fastapi import UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, join, update, desc, asc
import Model.user
import random
from Model.db import dbSession, dbSessionread
from Model.user import User,Session,Product,Order,Shop,Comment,Dialogue
from Type.function import get_time_now
from Type.product import product_add_interface, ProductBuy, comment_add, Productcheck, comment_del, pro_refund
from Service.user import UserModel
from Type.shop import pro_update

usermodel = UserModel()

class ProductModel(dbSession, dbSessionread):

    def add_product(self, obj: product_add_interface):  # 管理员添加一个商品
        try:
            obj_dict = jsonable_encoder(obj)
            product_add = Product(**obj_dict)
            with self.get_db() as session:
                session.add(product_add)
                session.commit()
                return product_add.id
        except Exception as e:
            # 如果添加失败，回滚会话以取消之前的操作
            session.rollback()
            # 返回自定义的错误类实例，包含错误信息
            raise str(e)

    def update_product(self, id: int, update_data: dict):  # 更新商品信息
        with self.get_db() as session:
            session.query(Product).filter(Product.id == id).update(update_data)
            session.commit()
            return id

    def delete_product(self, tt: comment_del):  # 删除商品
        with self.get_db() as session:
            product = session.query(Product).filter(Product.id == tt.comment_id).first()
            if product:
                product.status = 0
                session.commit()
                return 1
            else:
                return 0

    def get_product_by_id(self, id: int):  # 根据商品ID查询商品信息
        with self.get_db_read() as session:
            product = session.query(Product).filter(Product.id == id).first()
            return product

    def get_products_by_category(self, category: str):  # 根据商品类别查询商品列表
        with self.get_db_read() as session:
            products = session.query(Product).filter(Product.category == category).all()
            return products

    def get_products_by_price_range(self, min_price: float, max_price: float):  # 根据价格范围查询商品列表
        with self.get_db_read() as session:
            products = session.query(Product).filter(Product.price >= min_price, Product.price <= max_price).all()
            return products

    def get_products_by_name(self, name: str):  # 根据商品名称查询商品列表
        with self.get_db_read() as session:
            products = session.query(Product).filter(Product.name.like(f'%{name}%'), Product.status == 1).all()
            return products

    def get_bigpicture_product(self):
        with self.get_db_read() as session:
            products = session.query(Product).limit(5).all()
            return products

    def update_pro(self, temp: pro_update):
        with self.get_db_read() as session:
            try:
                product = session.query(Product).filter(Product.id == temp.product_id).first()

                # 如果找到了产品
                if product:
                    # 更新产品的非空属性
                    if temp.name is not None:
                        product.name = temp.name
                    if temp.description is not None:
                        product.description = temp.description
                    if temp.price is not None:
                        product.price = temp.price
                    if temp.category is not None:
                        product.category = temp.category
                    if temp.shop_id is not None:
                        product.shop_id = temp.shop_id
                    if temp.stock is not None:
                        product.stock = temp.stock
                    if temp.category is not None:
                        product.category = temp.category
                    if temp.image is not None:
                        if temp.image.content_type.startswith('application'):
                            usermodel.save_upload_file(temp.image, f"F:\\fastApiProject\static\\product_photo/{temp.image.filename}")  # 保存文件到指定位置
                        temp.image = "/static/product_photo/" + temp.image.filename
                        print(temp.image)
                        product.picture = temp.image

                    # 提交修改
                    session.commit()
            except Exception as e:
                # 处理异常
                session.rollback()  # 回滚事务
                print("更新产品时发生异常:", e)
            finally:
                session.close()  # 关闭会话，释放资源

    def get_total_products_count(self):  # 获取商品总数
        with self.get_db_read() as session:
            total_count = session.query(Product).count()
            return total_count

    def get_products(self, category: int, limit:int = 10):  # 获取前几个产品
        Products = []
        with self.get_db_read() as session:
            products = session.query(Product).filter(Product.category == category, Product.status == 1).all()
            random.shuffle(products)
            for product in products:
                Products.append(product)
                limit = limit - 1
                if limit == 0:
                    break
            return Products

    def get_all_products(self):
        with self.get_db_read() as session:
            products = session.query(Product).all()
            return products

    def get_products_shop(self,shop_id : int):
        with self.get_db_read() as session:
            products = session.query(Product).filter(Product.id == shop_id).all()
            return products

    def save_upload_file(self, upload_file: UploadFile, destination: str):
        with open(destination, "wb") as file_object:
            shutil.copyfileobj(upload_file.file, file_object)

    def purchase_product(self, buy_pro : ProductBuy):
        try:
            with self.get_db() as session:
                # 查询商品是否存在
                product = session.query(Product).filter(Product.id == ProductBuy.pro_id).first()
                if product is None:
                    raise ValueError("Product not found")

                # 检查库存是否足够
                if product.stock < ProductBuy.number:
                    raise ValueError("Not enough stock available")

                # 减少库存量
                product.stock -= ProductBuy.number
                temp = self.get_product_by_id(ProductBuy.user_id);
                order = Order(
                    product_id = ProductBuy.pro_id,
                    user_id = buy_pro.user_id,
                    quantity = buy_pro.number,
                    amount = temp.price * buy_pro.number,
                    address =  UserModel.get_user_by_id(ProductBuy.user_id).address,
                    status = 1,  # 假设初始状态为1，表示订单已创建
                    create_dt=func.now()
                )
                # 添加订单到数据库
                session.add(order)
                session.commit()
                return order.id

        except Exception as e:
            # 如果购买失败，回滚会话以取消之前的操作
            session.rollback()
            # 返回错误信息
            raise e

    def add_shop(self, shop_name: str):
        with self.get_db_read() as session:
            NewShop = Shop(name=shop_name, user_id=1)
            session.add(NewShop)
            session.commit()

    def add_comment(self, temp_comment: comment_add):
        tt = usermodel.get_finished_order_by_id(temp_comment.user_id, temp_comment.product_id)
        if tt == None:
            return 'error'
        else:
            obj_dict = jsonable_encoder(temp_comment)
            cc = Comment(review=obj_dict.get('review'), product_id=obj_dict.get('product_id'), user_id=obj_dict.get('user_id'))
            with self.get_db_read() as session:
                session.add(cc)
                session.commit()
            return cc.product_id

    def search_all_products(self, shop_id: int):
        with self.get_db_read() as session:
            query = session.query(Product).filter(
                Product.shop_id == shop_id, Product.status == 1
            ).all()
            ans = {
                "Products" : []
            }
            for item in query:
                order = session.query(Order).filter(
                    Order.product_id == item.id
                ).count()
                product = {
                    "id": item.id,
                    "name": item.name,
                    "time": str(item.creation_time),
                    "price": item.price,
                    "remaining_quantity": item.stock,
                    "description": item.description,
                    "image": item.picture,
                    "about_orders": order
                }
                ans["Products"].append(product)
            return ans

    def shopkeeper_add_product(self, description: str, price: float, name: str, shop_id: int, stock: int, image, category_id: int):
        with self.get_db_read() as session:
            try:
                # 检查文件类型
                if image.content_type.startswith('application'):
                    # 保存文件到指定位置
                    self.save_upload_file(image, f"static/product_photo/{image.filename}")
                    image_url = urljoin("", f"/static/product_photo/{image.filename}")
                else:
                    return "Not image"
            except Exception as e:
                return str(e)
            new_product = Product(name=name, price=price, shop_id=shop_id, stock=stock, description=description,
                                  picture=image_url, status=0, category = category_id)
            session.add(new_product)
            session.commit()
            return "OK"

    def purchase_product1(self, buy_pro: ProductBuy):

        obj_dict = jsonable_encoder(buy_pro)
        try:
            with self.get_db() as session:
                # 查询商品是否存在
                product = session.query(Product).filter(Product.id == buy_pro.product_id).first()
                if product is None:
                    return 0

                # 检查库存是否足够
                if product.stock < buy_pro.number:
                    return 1
                # 减少库存量
                product.stock -= buy_pro.number
                shop_id = product.shop_id
                shop = session.query(Shop).filter(Shop.id == shop_id).first()
                session.query(Product).filter(Product.id == obj_dict.get('product_id')).update({"stock": product.stock})
                session.commit()
                session.query(Shop).filter(Shop.id == shop_id).update({"sales_volume": shop.sales_volume + product.price})
                session.commit()
                temp = self.get_product_by_id(buy_pro.product_id)
                order = Order(
                    product_id=obj_dict.get('product_id'),
                    user_id=obj_dict.get('user_id'),
                    quantity=obj_dict.get('number'),
                    amount=temp.price * obj_dict.get('number'),
                    address= shop.address,
                    status = 1,  # 假设初始状态为1，表示订单已创建
                    create_dt=func.now()
                )
                # 添加订单到数据库
                session.add(order)
                session.commit()
                return 2

        except Exception as e:
            # 如果购买失败，回滚会话以取消之前的操作
            session.rollback()
            # 返回错误信息
            raise e

    def purchase_product2(self, buy_pro: ProductBuy):
        obj_dict = jsonable_encoder(buy_pro)
        try:
            with self.get_db() as session:
                # 查询商品是否存在
                product = session.query(Product).filter(Product.id == buy_pro.product_id).first()

                temp = self.get_product_by_id(buy_pro.product_id)
                order = Order(
                    product_id=obj_dict.get('product_id'),
                    user_id=obj_dict.get('user_id'),
                    quantity=obj_dict.get('number'),
                    amount=temp.price * obj_dict.get('number'),
                    address=usermodel.get_address_by_id(buy_pro.user_id),
                    status=0,  # 假设初始状态为1，表示订单已创建
                    create_dt=func.now()
                )
                # 添加订单到数据库
                session.add(order)
                session.commit()

                return order.id

        except Exception as e:
            # 如果购买失败，回滚会话以取消之前的操作
            session.rollback()
            # 返回错误信息
            raise e

    def purchase_product3(self, buy_pro: Productcheck):
        obj_dict = jsonable_encoder(buy_pro)
        try:
            with self.get_db() as session:
                # 查询商品是否存在
                product = session.query(Product).filter(Product.id == buy_pro.product_id).first()
                if product is None:
                    return 0

                # 检查库存是否足够
                if product.stock < buy_pro.number:
                    return 1

                # 减少库存量
                shop_id = product.shop_id
                shop = session.query(Shop).filter(Shop.id == shop_id).first()
                session.query(Product).filter(Product.id == obj_dict.get('product_id')).update({"stock": product.stock})
                session.commit()
                session.query(Shop).filter(Shop.id == shop_id).update({"sales_volume": shop.sales_volume + product.price})
                session.commit()

                product.stock -= buy_pro.number
                session.query(Product).filter(Product.id == obj_dict.get('product_id')).update({"stock": product.stock})
                session.commit()
                with self.get_db() as session:
                    session.query(Order).filter(Order.id == buy_pro.order_id, Order.user_id == buy_pro.user_id).update({"status": 1})
                    session.commit()
                    return 2
                # 添加订单到数据库

        except Exception as e:
            # 如果购买失败，回滚会话以取消之前的操作
            session.rollback()
            # 返回错误信息
            raise e

    def search_comment(self,temp:str):
        with self.get_db_read() as session:
            cc = session.query(Comment).filter(Comment.review.like(f'%{temp}%')).all()
            return cc

    def get_comment(self, id: int):
        with self.get_db_read() as session:
            cc = session.query(Comment).filter(Comment.product_id == id).all()
            return cc

    def get_status_f_orderid(self, order_id: int):
        with self.get_db_read() as session:
            order = session.query(Order).filter(Order.id == order_id).first()
            return order

    def refund_deal(self, product_id: int, num: int, salesum: float, order_id: int):
        with self.get_db_read() as session:
            Pro = session.query(Product).filter(Product.id == product_id).first()
            temp1 = Pro.shop_id
            Pro.stock += num
            session.commit()
        with self.get_db_read() as session:
            shop = session.query(Shop).filter(Shop.id == temp1).first()
            shop.sales_volume -= salesum
            session.commit()
        with self.get_db_read() as session:
            session.query(Order).filter(Order.id ==order_id).update({"status": 4})
            session.commit()

    def get_category_of_product(self, product_id: int):
        with self.get_db_read() as session:
            product = session.query(Product).filter(Product.id == product_id).first()
            return product.category

    def change_preference(self, preference: str):
        ones_indices = [i + 1 for i, char in enumerate(preference) if char == '1']
        if not ones_indices:
            return preference
        index_to_replace = random.choice(ones_indices)
        s_list = list(preference)
        s_list[index_to_replace - 1] = '0'
        return ''.join(s_list)

    def sell_out(self, product_id: int):
        with self.get_db_read() as session:
            session.query(Product).filter(Product.id == product_id).update({"status": 3}) # 3是待通过
            session.commit()

    def reapply(self, product_id: int):
        with self.get_db_read() as session:
            session.query(Product).filter(Product.id == product_id).update({"status": 3}) # 2是待审核
            session.commit()

    def add_dialog(self, send_id, receive_id: int, dialog: str):
        with self.get_db_read() as session:
            NewDialog = Dialogue(content=dialog, send_user_id=send_id, receive_user_id=receive_id)
            session.add(NewDialog)
            session.commit()

    def get_dialog(self, send_id: int, receive_id: int):
        with self.get_db_read() as session:
            dialog1 = session.query(Dialogue).filter(
                Dialogue.send_user_id.in_([send_id, receive_id])
            ).order_by(asc(Dialogue.create_dt)).all()
            temp_list = []
            result = {}
            for item in dialog1:
                if item.send_user_id == send_id:
                    temp_list.append({"status": 0,
                                      "content": item.content,
                                      "create_dt": jsonable_encoder(item.create_dt)})
                else:
                    temp_list.append({"status": 1,
                                      "content": item.content,
                                      "create_dt": jsonable_encoder(item.create_dt)})
                result["dialog"] = temp_list
            return result

    def get_shop_user_id(self, shop_id: int):
        with self.get_db_read() as session:
            shop = session.query(Shop).filter(Shop.id == shop_id).first()
            return shop.user_id

    def get_shop_dialog_user_id(self, shop_id: int):
        with self.get_db_read() as session:
            shop = session.query(Shop).filter(
                Shop.id == shop_id
            ).first()
            user = session.query(User).join(
                Dialogue,
                Dialogue.send_user_id == User.id
            ).filter(
                Dialogue.receive_user_id == shop.user_id,
            ).all()
            temp = []
            for item in user:
                temp.append({"username": item.username, "user_id": item.id})
            return temp