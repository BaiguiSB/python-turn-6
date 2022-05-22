from . import order
from ..user.backend import *
from ..market.backend import *
from .backend import *


@order.route("/", methods=["GET"])
def get_orders():
    statue = request.args.get("statue", None, int)
    if statue is not None:
        orders = get_all_orders(statue=statue)
        res = []
        if statue == 0:  # 未结单
            for _order in orders:
                res.append({"id": _order.id, "fid": _order.fid, "customer": _order.customer,
                            "statue": _order.statue, "start_time": _order.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "address": _order.address})
            return CreateJson(200, "OK", res)

        elif statue == 1:  # 完结撒花
            for _order in orders:
                res.append({"id": _order.id, "fid": _order.fid, "customer": _order.customer, "driver": _order.driver,
                            "statue": _order.statue, "start_time": _order.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "end_time": _order.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "driver_profit": _order.driver_profit.__str__(), "address": _order.address})

            return CreateJson(200, "OK", res)

        elif statue == 2:  # 派送中
            for _order in orders:
                res.append({"id": _order.id, "fid": _order.fid, "customer": _order.customer, "driver": _order.driver,
                            "statue": _order.statue, "start_time": _order.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "address": _order.address})

            return CreateJson(200, "OK", res)

    return CreateJson(400, "传入参数不存在")


@order.route("/", methods=["POST"])
def submit_orders():
    current_user = get_current_user()
    if current_user is not None:
        fid = request.args.get("fid", None, int)
        food_handle = get_food(fid)
        if food_handle is not None:
            address = request.args.get("address", None, str)
            if address is not None:
                order_id = add_order(fid, food_handle.master, current_user.id, address)
                return CreateJson(200, "OK", {"order_id": order_id})
            else:
                return CreateJson(400, "传入参数不存在")
        else:
            return CreateJson(400, "购买的食物不存在")
    else:
        return CreateJson(400, "未登录")


@order.route("/<int:oid>", methods=["PUT"])
def accept_order(oid: int):
    current_user = get_current_user()
    if current_user is not None:
        if current_user.role_id == 2:
            target_order = get_order(oid)
            if target_order is not None:
                driver_accept_order(oid, current_user.id)
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "目标订单不存在")
        else:
            return CreateJson(400, "角色错误")
    else:
        return CreateJson(400, "未登录")


@order.route("/<int:oid>", methods=["DELETE"])
def cancel_or_finish_order(oid: int):
    current_user = get_current_user()
    target_order = get_order(oid)
    if current_user is not None:
        if target_order is not None:
            if current_user.id == target_order.customer and target_order.statue == 0:
                cancel_raw_order(oid)
                return CreateJson(200, "OK")
            elif current_user.id == target_order.driver and target_order.statue == 2:
                finish_order(oid)
                return CreateJson(200, "OK")
            else:
                return CreateJson(400, "角色错误")
        else:
            return CreateJson(400, "目标订单不存在")
    else:
        return CreateJson(400, "未登录")


@order.route("/chat-token", methods=["GET"])
def get_all_token():
    current_user = get_current_user()
    if current_user is not None:
        tokens = get_token(current_user.role_id, current_user.id)
        return CreateJson(200, "OK", {"tokens": tokens})
    else:
        return CreateJson(400, "未登录")
