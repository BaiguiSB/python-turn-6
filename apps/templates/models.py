from . import db
from hashlib import md5


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, default=1)
    username = db.Column(db.VARCHAR(20), unique=True)
    password_hash = db.Column(db.VARCHAR(32), nullable=False)
    email = db.Column(db.VARCHAR(32), nullable=False)
    sex = db.Column(db.Boolean, nullable=True, default=0)
    head = db.Column(db.VARCHAR(32))
    subscribe_other = db.Column(db.VARBINARY(256))
    subscribe_me = db.Column(db.VARBINARY(256))
    collection = db.Column(db.VARBINARY(256))

    @property
    def password(self):
        return None

    @password.setter
    def password(self, password):
        self.password_hash = md5(password.encode()).hexdigest()

    def verify_password(self, password):
        if self.password_hash == md5(password.encode()).hexdigest():
            return True
        else:
            return False


class Food(db.Model):
    __tablename__ = "foods"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(32), nullable=False)
    master = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL, nullable=False)

    image = db.Column(db.VARCHAR(32), default="")
    likes = db.Column(db.Integer, default=0)
    collect = db.Column(db.Integer, default=0)


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    food_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.VARCHAR(256), nullable=False)
    author = db.Column(db.Integer, nullable=False)


class Sub_comments(db.Model):
    __tablename__ = "sub_comments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    root_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.VARCHAR(256), nullable=False)
    author = db.Column(db.Integer, nullable=False)


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fid = db.Column(db.Integer, nullable=False)
    store = db.Column(db.Integer, nullable=False)
    customer = db.Column(db.Integer, nullable=False)
    driver = db.Column(db.Integer)
    room = db.Column(db.VARCHAR(32), nullable=False)

    # 订单状态 0：未接单，1：完成，2：派送中
    statue = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    driver_profit = db.Column(db.DECIMAL)
    address = db.Column(db.VARCHAR(128), nullable=False)
