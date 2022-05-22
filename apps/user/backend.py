import json
import os
import pickle
from itsdangerous import TimedJSONWebSignatureSerializer, BadTimeSignature, SignatureExpired
from flask import Response, request, current_app
from ..templates.models import User, Food
from ..templates import db
from ..templates.email import send_check_main


def CreateJson(statue, message, data=None):
    if data is None:
        data = list()
    res = dict()
    res["statue"] = statue
    res["message"] = message
    res["data"] = data
    return Response(json.dumps(res), mimetype='application/json')


def is_exist(uid):
    user = User.query.filter_by(id=uid).all()
    if user.__len__() != 0:
        return user[0]
    else:
        return None


def get_current_user():
    if request.headers.get("token") is not None:
        serializer = TimedJSONWebSignatureSerializer(
            current_app.config["SECRET_KEY"],
            expires_in=current_app.config["EXPIRATION"])
        try:
            token = serializer.loads(request.headers.get("token"))
        except BadTimeSignature:
            return None
        token = dict(token)
        return is_exist(token["id"])
    return None


def login_required(func):
    def token_check_success(*args, **kwargs):
        func(*args, **kwargs)

    def token_check_fail():
        return CreateJson(403, "Forbidden")

    if request.headers.get("token") is not None:
        serializer = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"],
                                                     expires_in=current_app.config["EXPIRATION"])
        try:
            token = serializer.dumps(request.headers.get("token"))
        except (BadTimeSignature, SignatureExpired):
            return token_check_fail
        token = dict(token)
        if User.query.filter_by(id=token["id"]).all().__len__() == 0:
            return token_check_fail

        return token_check_success
    return token_check_fail


def login(username, password):
    user = User.query.filter_by(username=username).all()
    if user.__len__() != 0:
        user = user[0]
        if user.verify_password(password):
            serializer = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"],
                                                         expires_in=current_app.config["EXPIRATION"])
            return serializer.dumps({"id": user.id}).decode()
    return None


# 0普通用户 1商家 2棋手 4管理员
# 4:用户侧管理员 5:商品侧管理员
def register(username, password, email, role_id=0, sex=0):
    if User.query.filter_by(username=username).all().__len__() != 0:
        return None  # 已经注册过了
    new_user = User(username=username, password=password, role_id=role_id, email=email, sex=sex, head="",
                    subscribe_other=pickle.dumps([]), subscribe_me=pickle.dumps([]),
                    collection=pickle.dumps([]))
    db.session.add(new_user)
    db.session.commit()
    return new_user


def cancellation(user_id):
    if User.query.filter_by(id=user_id).all().__len__() == 0:
        return None
    db.session.delete(User.query.filter_by(id=user_id).all()[0])
    db.session.commit()


def send_reset_mail(user_id: int, address: str, new_pass: str):
    serializer = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"],
                                                 expires_in=current_app.config["EXPIRATION"])
    token = serializer.dumps({"user_id": user_id, "new_pass": new_pass}).encode()
    send_check_main(address, token)
    return


def check_reset(token):
    serializer = TimedJSONWebSignatureSerializer(current_app.config["SECRET_KEY"],
                                                 expires_in=current_app.config["EXPIRATION"])
    try:
        data = serializer.loads(token)
        data = dict(data)
    except (BadTimeSignature, SignatureExpired):
        return False
    set_password(data["user_id"], data["new_pass"])
    return True


def set_password(user_id, password):
    user = User.query.filter_by(id=user_id).all()[0]
    user.password = password
    db.session.add(user)
    db.session.commit()


def set_sex(user_id, sex):
    user = User.query.filter_by(id=user_id).all()[0]
    user.sex = bool(sex)
    db.session.add(user)
    db.session.commit()


def set_head(user_id, path):
    user = User.query.filter_by(id=user_id).all()[0]
    if user.head != "" and os.path.exists(current_app.config["FILE_PATH"] + user.head + ".png"):
        os.remove(current_app.config["FILE_PATH"] + user.head + ".png")

    user.head = path
    db.session.add(user)
    db.session.commit()


def subscribe(uid, tid):
    t_user = User.query.filter_by(id=tid).all()[0]
    m_user = User.query.filter_by(id=uid).all()[0]
    t_user_subscribe_me = list(pickle.loads(t_user.subscribe_me))
    m_user_subscribe_other = list(pickle.loads(m_user.subscribe_other))
    if tid not in m_user_subscribe_other:
        m_user_subscribe_other += [tid]
        m_user.subscribe_other = pickle.dumps(m_user_subscribe_other)
        db.session.add(m_user)
    if uid not in t_user_subscribe_me:
        t_user_subscribe_me += [uid]
        t_user.subscribe_me = pickle.dumps(t_user_subscribe_me)
        db.session.add(t_user)
    db.session.commit()


def de_subscribe(uid, tid):
    t_user = User.query.filter_by(id=tid).all()[0]
    m_user = User.query.filter_by(id=uid).all()[0]
    t_user_subscribe_me = list(pickle.loads(t_user.subscribe_me))
    m_user_subscribe_other = list(pickle.loads(m_user.subscribe_other))
    if tid in m_user_subscribe_other:
        m_user_subscribe_other.remove(tid)
        m_user.subscribe_other = pickle.dumps(m_user_subscribe_other)
        db.session.add(m_user)
    if uid in t_user_subscribe_me:
        t_user_subscribe_me.remove(uid)
        t_user.subscribe_me = pickle.dumps(t_user_subscribe_me)
        db.session.add(t_user)
    db.session.commit()


def collect_food(uid: int, fid: int):
    user = User.query.filter_by(id=uid).all()[0]
    food = Food.query.filter_by(id=fid).all()[0]

    user_collections = pickle.loads(user.collection)
    if fid not in user_collections:
        food.collect += 1
        db.session.add(food)
        db.session.commit()

        user_collections.append(fid)
        user.collection = pickle.dumps(user_collections)
        db.session.add(user)
        db.session.commit()

