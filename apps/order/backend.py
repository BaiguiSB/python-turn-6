import datetime
from ..templates.models import *
from ..templates import db
from decimal import Decimal
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer


def get_all_orders(statue: int):
    return list(Order.query.filter_by(statue=statue).all())


def get_order(oid: int):
    order = Order.query.filter_by(id=oid).all()
    if order.__len__():
        return order[0]
    else:
        return None


def add_order(fid: int, store: int, customer: int, address: str):
    new_order = Order(fid=fid, store=store, customer=customer, statue=0, start_time=datetime.datetime.now(),
                      address=address, room=md5(datetime.datetime.now().__str__().encode()).hexdigest())
    db.session.add(new_order)
    db.session.commit()
    return new_order.id


def cancel_order(oid: int):
    order = Order.query.filter_by(id=oid).all()[0]
    db.session.delete(order)
    db.session.commit()


def driver_accept_order(oid: int, uid: int):
    order = Order.query.filter_by(id=oid).all()[0]
    order.driver = uid
    order.statue = 2
    db.session.add(order)
    db.session.commit()


def finish_order(oid: int):
    order = Order.query.filter_by(id=oid).all()[0]
    order.end_time = datetime.datetime.now()
    order.statue = 1

    food = Food.query.filter_by(id=order.fid).all()[0]

    order.driver_profit = food.price * current_app.config["PROFIT_FACTOR"]
    db.session.add(order)
    db.session.commit()


def cancel_raw_order(oid: int):
    order = Order.query.filter_by(id=oid).all()[0]
    db.session.delete(order)
    db.session.commit()


def get_profit(uid):
    orders = Order.query.filter_by(driver=uid).all()
    total = Decimal("0")
    for order in orders:
        total += order.driver_profit
    return total


def get_token(role: int, tid: int):
    res = []
    orders = []
    username = ""
    serializer = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"],
                                                 expires_in=current_app.config["EXPIRATION"])
    if role == 0:
        username = "用户"
        orders = Order.query.filter_by(customer=tid).all()
    elif role == 1:
        username = "商家"
        orders = Order.query.filter_by(store=tid).all()
    elif role == 2:
        username = "骑手"
        orders = Order.query.filter_by(driver=tid).all()
    elif role == 4:
        username = "管理员"

    for order in orders:
        if order.statue != 1:
            res.append({"oid": order.id, "token": serializer.dumps({"room": order.room, "name": username}).decode()})
    return res
