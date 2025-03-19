from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    VARCHAR,
    ForeignKey, Date, Index, Float, event, func,
)

from Model.db import Base

class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        Index('ix_user_has_delete_username', "has_delete", "username"),  # 非唯一的联合索引
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')  # 主键
    username = Column(VARCHAR(32), nullable=False, unique=True, comment='用户名')  # 用户名，非空，唯一
    password = Column(VARCHAR(128), nullable=False, comment='密码')  # 密码，非空
    photo = Column(VARCHAR(128),nullable=True, comment='头像')
    address = Column(VARCHAR(256), nullable=True, comment='地址')  # 地址，可空
    registration_dt = Column(DateTime, nullable=False, comment='注册时间', default=func.now())  # 注册时间，非空
    phone_number = Column(VARCHAR(32), nullable=True, unique=True, comment='电话号码')  # 电话号码，可空，唯一
    id_card_number = Column(VARCHAR(32), nullable=True, unique=True, comment='身份证号')  # 身份证号，可空，唯一
    identity_type = Column(Integer, nullable=False, comment='身份区分')  # 身份区分，非空
    has_delete = Column(Integer, nullable=False, comment='是否已经删除', default=0)  # 是否被删除，非空
    preference = Column(Integer, nullable=False, default = 0)

class Session(Base):  # session表
    __tablename__ = 'session'
    __table_args__ = (
        Index('ix_session_has_delete_token_s6', "has_delete", "token_s6"),  # 非唯一的联合索引
        Index('ix_session_has_delete_token', "has_delete", "token"),  # 非唯一的联合索引
        Index('ix_session_func_type_has_delete', "func_type", "has_delete"),  # 非唯一的联合索引
    )
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')  # 主键
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True, comment='外键，用户id')  # 外键，用户id，非空，索引
    file_id = Column(Integer,  nullable=True, index=True,
                     comment='文件id')  # 外键，文件id，可空，索引
    token = Column(VARCHAR(32), unique=True, nullable=False, comment='session唯一识别串')  # token，非空，唯一
    token_s6 = Column(VARCHAR(16), nullable=True, comment='8位短token')  # 邮箱验证码，非空
    use = Column(Integer, nullable=False, comment='使用次数')  # 使用次数，非空
    use_limit = Column(Integer, nullable=True, comment='限制次数，没有限制即为NULL')  # 限制次数，可空
    exp_dt = Column(DateTime, comment='过期时间', nullable=False)  # 过期时间，非空
    ip = Column(VARCHAR(32), comment='客户端ip')  # ip
    user_agent = Column(VARCHAR(256), comment='客户端信息')  # 客户端信息
    create_dt = Column(DateTime, comment='创建时间', default=func.now())  # 创建时间
    func_type = Column(Integer,
                       comment='0 用户登录 session:1 用户邮箱验证 session,2 文件下载 session,3 文件上传 session')  # 操作类型
    has_delete = Column(Integer, nullable=False, comment='是否已经删除', default=0)  # 是否已经删除



class Shop(Base):
    __tablename__ = 'shop'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')  # 主键
    name = Column(VARCHAR(64), nullable=False, comment='名称')  # 名称，非空
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='用户id')  # 用户id，非空，外键关联user表的id字段
    creation_time = Column(DateTime, nullable=False, comment='创建时间', default=func.now())  # 创建时间，非空，默认为当前时间
    sales_volume = Column(Float, nullable=False, default=0, comment='销售额')  # 销售额，非空，默认为0
    picture = Column(VARCHAR(64), nullable=True, comment='图片') # 商铺图片
    address = Column(VARCHAR(256), nullable=True, comment='地址')  # 地址，可空
    status = Column(Integer, nullable=False, comment='状态')

class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')  # 主键
    name = Column(VARCHAR(64), nullable=False, comment='名称')  # 名称，非空
    category = Column(VARCHAR(64), nullable=False, comment='分类')  # 分类，非空
    price = Column(Float, nullable=False, comment='价格')  # 价格，非空
    shop_id = Column(Integer, ForeignKey('shop.id'), nullable=False, comment='所属店铺id')  # 所属店铺id，非空，外键关联shop表的id字段
    stock = Column(Integer, nullable=False, comment='库存')
    picture = Column(VARCHAR(64),nullable=True, comment='图片')
    description = Column(VARCHAR(64), nullable=True, comment='描述')
    status = Column(Integer, nullable=False, comment='状态')
    creation_time = Column(DateTime, nullable=False, comment='创建时间', default=func.now())  # 创建时间，非空，默认为当前时间

class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')  # 主键
    status = Column(Integer, nullable=False, comment='状态')  # 状态，非空
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False, comment='商品id')  # 商品id，非空，外键关联product表的id字段
    address = Column(VARCHAR(256), nullable=False, comment='地址')  # 地址，非空
    quantity = Column(Integer, nullable=False, comment='数量')  # 数量，非空
    amount = Column(Float, nullable=False, comment='金额')  # 金额，非空
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='用户id')  # 用户id，非空，外键关联user表的id字段
    create_dt = Column(DateTime, comment='创建时间', default=func.now())  # 创建时间

class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')  # 主键
    review = Column(VARCHAR(256), nullable=False, comment='评价')  # 评价，非空
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False, comment='商品id')  # 商品id，非空，外键关联product表的id字段
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='用户id')  # 用户id，非空，外键关联user表的id字段
    create_dt = Column(DateTime, comment='创建时间', default=func.now())  # 创建时间

class Dialogue(Base):
    __tablename__ = 'dialogue'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键')  # 主键
    content = Column(VARCHAR(256), nullable=False, comment='对话内容')
    send_user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='发送用户id')
    receive_user_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment='接受用户id')
    create_dt = Column(DateTime, comment='创建时间', default=func.now())  # 创建时间