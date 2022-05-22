from ..templates.models import *
from ..templates import db
import os
from flask import current_app
from decimal import Decimal


def add_foods(master: int, name: str, price: str):
    new_food = Food(master=master, name=name, price=Decimal(price), image="")
    db.session.add(new_food)
    db.session.commit()
    return new_food


def delete_foods(food_id: int):
    food = Food.query.filter_by(id=food_id).all()[0]
    for comment in Comments.query.filter_by(food_id=food_id).all():
        for sub_comment in Sub_comments.query.filter_by(root_id=comment.id).all():
            db.session.delete(sub_comment)
            db.session.commit()
        db.session.delete(comment)
        db.session.commit()
    db.session.delete(food)
    db.session.commit()


def food_likes(food_id: int):
    food = Food.query.filter_by(id=food_id).all()[0]
    food.likes += 1
    db.session.add(food)
    db.session.commit()


def food_set_image(food_id: int, name: str):
    food = Food.query.filter_by(id=food_id).all()[0]
    if food.image != "" and os.path.exists(current_app.config["FILE_PATH"] + food.image + ".png"):
        os.remove(current_app.config["FILE_PATH"] + food.image + ".png")
    food.image = name
    db.session.add(food)
    db.session.commit()


def food_set_info(food_id: int, name: str = None, price: str = None):
    food = Food.query.filter_by(id=food_id).all()[0]
    if name is not None:
        food.name = name
    if price is not None:
        food.price = Decimal(price)
    db.session.add(food)
    db.session.commit()


def get_food(food_id: int):
    food = Food.query.filter_by(id=food_id).all()
    if food.__len__():
        return food[0]
    return None


def add_comment(food_id: int, content: str, author: int):
    new_comment = Comments(food_id=food_id, content=content, author=author)
    db.session.add(new_comment)
    db.session.commit()
    return new_comment


def del_comment(comment_id: int):
    sub_comments = Sub_comments.query.filter_by(root_id=comment_id).all()
    for sub_comment in sub_comments:
        db.session.delete(sub_comment)
        db.session.commit()
    comment = Comments.query.filter_by(id=comment_id).all()[0]
    db.session.delete(comment)
    db.session.commit()


def is_comment_exist(cid: int):
    comment = Comments.query.filter_by(id=cid).all()
    if comment.__len__():
        return comment[0]
    return None


def add_sub_comment(root_id: int, content: str, author: int):
    new_comment = Sub_comments(root_id=root_id, content=content, author=author)
    db.session.add(new_comment)
    db.session.commit()
    return new_comment


def del_sub_comment(comment_id: int):
    sub_comment = Sub_comments.query.filter_by(id=comment_id).all()[0]
    db.session.delete(sub_comment)
    db.session.commit()


def is_sub_comment_exist(cid: int):
    comment = Sub_comments.query.filter_by(id=cid).all()
    if comment.__len__():
        return comment[0]
    return None


def get_comments(food_id: int):
    comments = Comments.query.filter_by(food_id=food_id).all()
    res = []
    for comment in comments:
        sub_comments = Sub_comments.query.filter_by(root_id=comment.id).all()
        sub_comments_list = []
        for sub_comment in sub_comments:
            sub_comments_list.append(
                {"id": sub_comment.id, "author": sub_comment.author, "content": sub_comment.content})
        res.append(
            {"id": comment.id, "author": comment.author, "content": comment.content, "sub_comments": sub_comments_list})
    return res
