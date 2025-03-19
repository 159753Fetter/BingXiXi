from sqlalchemy import create_engine

from const import SQLALCHEMY_DATABASE_URL,SQLALCHEMY_DATABASE_URL_MASTER

# 这里需要引入所有使用 Base 的 Model
from Model.user import *

create_table_list = [User, Session, Shop, Product, Order, Comment
                     ]

if __name__ == "__main__":
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    for tb in create_table_list:
        tb.__table__.create(bind=engine, checkfirst=True)

