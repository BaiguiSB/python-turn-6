from time import time
from hashlib import md5
import re
from flask import send_file, current_app
from . import user
from .backend import *
from ..order.backend import get_profit


@user.route('/', methods=["GET"])
def hello():
    return "hello"


@user.route('/<int:uid>', methods=["GET"])
def get_info(uid: int):
    target_user = is_exist(uid)
    if target_user is not None:
        raw_dict = {"id": uid, "username:": target_user.username, "email": target_user.email,
                    "sex": target_user.sex, "head": target_user.head,
                    "subscribe_other": pickle.loads(target_user.subscribe_other),
                    "subscribe_me": pickle.loads(target_user.subscribe_me),
                    "collections": pickle.loads(target_user.collection)}
        if target_user.role_id == 2:
            raw_dict["profit"] = get_profit(target_user.id).__str__()
        return CreateJson(200, "OK", raw_dict)
    return CreateJson(400, "目标用户不存在")


@user.route('/', methods=["POST"])
def api_register():
    username = request.args.get("username", default=None, type=str)
    password = request.args.get("password", default=None, type=str)
    email = request.args.get("email", default=None, type=str)
    role_id = request.args.get("role_id", default=None, type=int)

    if username is not None and password is not None and email is not None:
        if role_id is None:
            role_id = 1
        elif role_id not in [0, 1, 2]:
            return CreateJson(400, "身份错误")
        if re.match("^[A-Za-z0-9]+@[a-zA-Z0-9_-]+(.[a-zA-Z0-9_-]+)+$", email) is not None:
            res = register(username, password, email, role_id)
            if res is not None:
                return CreateJson(200, "OK", {"uid": res.id})
            return CreateJson(400, "用户名已经注册")
        return CreateJson(400, "邮箱格式错误")
    return CreateJson(400, "传参缺失")


@user.route('/<int:uid>', methods=["DELETE"])
def api_cancellation(uid: int):
    current_user = get_current_user()
    if current_user is not None:
        if uid == current_user.id or current_user.role_id == 4:
            cancellation(uid)
            return CreateJson(200, "OK")
        else:
            return CreateJson(400, "权限不足")
    else:
        return CreateJson(400, "未登录")


@user.route('/login', methods=["GET"])
def api_login():
    username = request.args.get("username", default=None, type=str)
    password = request.args.get("password", default=None, type=str)
    if username is not None and password is not None:
        token = login(username, password)
        if token is not None:
            return CreateJson(200, "OK", {"token": token})
        else:
            return CreateJson(400, "登录错误")
    else:
        return CreateJson(400, "传参错误")


@user.route('/<int:uid>/head', methods=["GET"])
def get_head(uid: int):
    target_user = is_exist(uid)
    if target_user is not None:
        if target_user.head == "":
            return send_file(current_app.config["FILE_PATH"] + "default.png")
        else:
            return send_file(current_app.config["FILE_PATH"] + target_user.head + ".png")
    else:
        return CreateJson(400, "目标用户不存在")


@user.route('/<int:uid>/head', methods=["PUT"])
def set_head(uid: int):
    current_user = get_current_user()
    if current_user is not None:
        if current_user.role_id == 4 or uid == current_user.id:
            f = request.files.get("head", default=None)
            if f is not None:
                filename = md5(time().__str__().encode()).hexdigest()
                f.save(current_app.config["FILE_PATH"] + filename + ".png")
                f.close()
                set_head(uid, filename)
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "未读取到图片")
        else:
            return CreateJson(400, "权限不足")
    else:
        return CreateJson(400, "未登录")


@user.route('/<int:uid>/sex', methods=["PUT"])
def set_sex(uid: int):
    current_user = get_current_user()
    if current_user is not None:
        if current_user.role_id == 4 or uid == current_user.id:
            sex = request.args.get("sex", default=None, type=bool)
            if sex is not None:
                set_sex(uid, sex)
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "未读取到参数")
        else:
            return CreateJson(400, "权限不足")
    else:
        return CreateJson(400, "未登录")


@user.route('/<int:uid>/password', methods=["PUT"])
def reset_password(uid: int):
    current_user = get_current_user()
    old_password = request.args.get("old", default=None, type=str)
    new_password = request.args.get("new", default=None, type=str)
    if current_user is not None:
        if old_password is not None and new_password is not None:
            if current_user.id == uid or current_user.role_id == 4:
                if current_user.verify_password(old_password):
                    send_reset_mail(uid, current_user.email)
                    return CreateJson(200, "OK")
                else:
                    return CreateJson(400, "密码错误")
            else:
                return CreateJson(400, "权限不足")
        else:
            return CreateJson(400, "未传入参数")
    else:
        return CreateJson(400, "未登录")


@user.route("/confirm/<token>")
def confirm_reset(token: str):
    if check_reset(token):
        return CreateJson(200, "OK")
    else:
        CreateJson(400, "认证失败")


@user.route('/<int:tid>/subscribe', methods=["POST"])
def set_subscribe(tid: int):
    current_user = get_current_user()
    target_user = is_exist(tid)
    if current_user is not None:
        if target_user is not None:
            if tid != current_user.id:
                subscribe(current_user.id, tid)
            return CreateJson(200, "OK")
        else:
            return CreateJson(400, "目标用户不存在")
    else:
        return CreateJson(400, "未登录")


@user.route('/<int:tid>/subscribe', methods=["GET"])
def get_subscribe(tid: int):
    target_user = is_exist(tid)
    if target_user is not None:
        return CreateJson(200, "OK",
                          {"my_subscribe": pickle.loads(target_user.subscribe_other),
                           "subscribe_me": pickle.loads(target_user.subscribe_me)})
    else:
        return CreateJson(400, "未登录")


@user.route('/<int:tid>/subscribe', methods=["DELETE"])
def cancel_subscribe(tid: int):
    current_user = get_current_user()
    target_user = is_exist(tid)
    uid = request.args.get("uid", None, int)
    if current_user is not None:
        if target_user is not None:
            if current_user.role_id == 4:
                if uid is not None:
                    if is_exist(uid) is not None:
                        de_subscribe(uid, tid)
                        return CreateJson(200, "OK")
                    else:
                        return CreateJson(400, "目标用户不存在")
                else:
                    return CreateJson(400, "目标用户不存在")
            elif tid != current_user.id:
                de_subscribe(current_user.id, tid)
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "权限不足")
        else:
            return CreateJson(400, "目标用户不存在")
    else:
        return CreateJson(400, "未登录")
