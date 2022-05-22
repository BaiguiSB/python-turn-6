from time import time
from flask import send_file
from . import market
from .backend import *
from ..user.backend import *


@market.route("/hello")
def hello():
    return "hello"


@market.route("/food", methods=["POST"])
def add_food():
    current_user = get_current_user()
    if current_user is not None and current_user.role_id == 1:
        name = request.args.get("name", None, str)
        price = request.args.get("price", None, str)
        if name is not None and price is not None:
            add_foods(current_user.id, name, price)
            return CreateJson(200, "OK")
        else:
            return CreateJson(400, "缺少请求参数")
    else:
        return CreateJson(403, "尚未登录或权限不足")


@market.route("/food/<int:fid>", methods=["DELETE"])
def del_food(fid: int):
    current_user = get_current_user()
    if current_user is not None:
        if fid is not None:
            food_handle = get_food(fid)
            if food_handle is not None:
                if food_handle.master == current_user.id or current_user.role == 4:
                    delete_foods(fid)
                    return CreateJson(200, "OK")
                else:
                    return CreateJson(400, "权限不足")
            else:
                return CreateJson(400, "目标食品不存在")
        else:
            return CreateJson(400, "参数错误")
    else:
        return CreateJson(400, "用户未登录")


@market.route("/food/<int:fid>", methods=["GET"])
def get_food_info(fid: int):
    food_handle = get_food(fid)
    if food_handle is not None:
        comments = get_comments(food_handle.id)
        return CreateJson(200, "OK",
                          {"name": food_handle.name, "price": str(food_handle.price), "master": food_handle.master,
                           "comments": comments, "likes": food_handle.likes, "collections": food_handle.collect})
    else:
        return CreateJson(400, "目标食品不存在")


@market.route("/food/<int:fid>", methods=["PUT"])
def edit_food(fid: int):
    food_handle = get_food(fid)
    current_user = get_current_user()
    if current_user is not None:
        if food_handle is not None:
            if food_handle.master == current_user.id or current_user.role_id == 5:
                food_set_info(fid, request.args.get("name", None, str), request.args.get("price", None, str))
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "权限不足")
        else:
            return CreateJson(400, "目标食品不存在")
    else:
        return CreateJson(400, "未登录")


@market.route("/food/<int:fid>/image", methods=["PUT"])
def edit_food_img(fid: int):
    food_handle = get_food(fid)
    current_user = get_current_user()
    if current_user is not None:
        if food_handle is not None:
            if food_handle.master == current_user.id or current_user.role_id == 5:
                image = request.files.get("image", default=None)
                if image is not None:
                    filename = md5(time().__str__().encode()).hexdigest()
                    image.save(current_app.config["FILE_PATH"] + filename + ".png")
                    image.close()
                    food_set_image(fid, filename)
                    return CreateJson(200, "OK")
                else:
                    return CreateJson(400, "无图片")
            else:
                return CreateJson(400, "无权限")
        else:
            return CreateJson(400, "目标食品不存在")
    else:
        return CreateJson(400, "未登录")


@market.route("/food/<int:fid>/image", methods=["GET"])
def get_food_img(fid: int):
    food_handle = get_food(fid)
    if food_handle is not None:
        if food_handle.image == "":
            return send_file(current_app.config["FILE_PATH"] + "default.png")
        else:
            return send_file(current_app.config["FILE_PATH"] + food_handle.image + ".png")
    else:
        return CreateJson(400, "目标食品不存在")


@market.route("/food/<int:fid>/comment", methods=["GET"])
def get_food_comment(fid: int):
    food_handle = get_food(fid)
    if food_handle is not None:
        return CreateJson(200, "OK", get_comments(fid))
    return CreateJson(400, "目标食品不存在")


@market.route("/food/<int:fid>/comment", methods=["POST"])
def add_food_comment(fid: int):
    food_handle = get_food(fid)
    current_user = get_current_user()
    if current_user is not None:
        if food_handle is not None:
            content = request.args.get("content", None, str)
            if content is not None:
                add_comment(fid, content, current_user.id)
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "无传入参数")
        else:
            return CreateJson(400, "目标食品不存在")
    else:
        return CreateJson(400, "未登录")


@market.route("/food/<int:fid>/comment/<int:cid>", methods=["DELETE"])
def del_food_comment(fid: int, cid: int):
    current_user = get_current_user()
    target_comment = is_comment_exist(cid)
    if current_user is not None:
        if target_comment is not None:
            if current_user.role_id == 5 or current_user.id == target_comment.author:
                del_comment(cid)
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "无权限")
        else:
            return CreateJson(400, "目标评论不存在")
    else:
        return CreateJson(400, "未登录")


@market.route("/food/<int:fid>/comment/<int:root_id>/sub_comment", methods=["POST"])
def add_food_sub_comment(fid: int, root_id: int):
    root_comment = is_comment_exist(root_id)
    current_user = get_current_user()
    if current_user is not None:
        if root_comment is not None:
            content = request.args.get("content", None, str)
            if content is not None:
                add_sub_comment(root_id, content, current_user.id)
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "目标评论不存在")
        else:
            return CreateJson(400, "父评论不存在")
    else:
        return CreateJson(400, "未登录")


@market.route("/food/<int:fid>/comment/<int:root_id>/sub_comment/<int:sub_id>", methods=["DELETE"])
def del_food_sub_comment(fid: int, root_id: int, sub_id: int):
    current_user = get_current_user()
    target_comment = is_sub_comment_exist(sub_id)
    if current_user is not None:
        if target_comment is not None:
            if current_user.role_id == 5 or current_user.id == target_comment.author:
                del_sub_comment(sub_id)
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "权限不足")
        else:
            return CreateJson(400, "目标评论不存在")
    else:
        return CreateJson(400, "未登录")


@market.route("/food/<int:fid>/like", methods=["GET"])
def food_like(fid: int):
    current_user = get_current_user()
    food = get_food(fid)
    if current_user is not None:
        if food is not None:
            food_likes(fid)
            return CreateJson(200, "OK")
        else:
            return CreateJson(400, "目标食物不存在")
    else:
        return CreateJson(400, "未登录")


@market.route("/food/<int:fid>/collect", methods=["GET"])
def food_collect(fid: int):
    current_user = get_current_user()
    food = get_food(fid)
    if current_user is not None:
        if food is not None:
            collect_food(current_user.id, fid)
            return CreateJson(200, "OK")
        else:
            return CreateJson(400, "目标食物不存在")
    else:
        return CreateJson(400, "未登录")


@market.route("/food/<int:fid>/share", methods=["GET"])
def food_share(fid: int):
    return CreateJson(200, "OK", {"url": "/api/v1/market/food/" + str(fid)})


@market.route("/food", methods=["GET"])
def search_and_recommend():
    key = request.args.get("key", None, str)
    page = request.args.get("page", 1, int)
    res = list()
    if key is None:
        for i in range((page - 1) * 5, page * 5):
            food_handle = get_food(i)
            if food_handle is not None:
                res.append({"name": food_handle.name, "price": str(food_handle.price), "master": food_handle.master,
                            "likes": food_handle.likes, "collections": food_handle.collect})
        return CreateJson(200, "OK", res)
    else:
        food_res = Food.query.filter(Food.name.like("%{key}%".format(key=key))).all()
        if (food_res.__len__() < page * 5) and (food_res.__len__() > (page - 1) * 5):
            for i in range((page - 1) * 5, food_res.__len__()):
                food_handle = food_res[i]
                res.append({"name": food_handle.name, "price": str(food_handle.price), "master": food_handle.master,
                            "likes": food_handle.likes, "collections": food_handle.collect})
        elif food_res.__len__() > page * 5:
            for i in range((page - 1) * 5, page * 5):
                food_handle = food_res[i]
                res.append({"name": food_handle.name, "price": str(food_handle.price), "master": food_handle.master,
                            "likes": food_handle.likes, "collections": food_handle.collect})
    return CreateJson(200, "OK", res)
