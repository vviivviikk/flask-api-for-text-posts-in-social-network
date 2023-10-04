from app import app, USERS, models
from flask import request, Response
import json
from http import HTTPStatus


@app.route("/")
def index():
    return "<h1>Hello World</h1>"


@app.route("/users/create", methods=["POST"])
def user_create():
    data = request.get_json()
    user_id = len(USERS)
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]

    if not models.User.is_valid_email(email):
        return Response(
            f"Вы ввели некорректный email: '{email}'", status=HTTPStatus.BAD_REQUEST
        )
    if not models.User.is_unique_email(email):
        return Response(
            f"email '{email}' уже используется другим пользователем",
            status=HTTPStatus.BAD_REQUEST,
        )

    user = models.User(user_id, first_name, last_name, email)
    USERS.append(user)
    response = Response(
        json.dumps(
            {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "total_reactions": user.total_reactions,
                "posts": user.posts,
            }
        ),
        HTTPStatus.CREATED,
        mimetype="application/json",
    )
    return response


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):

    if not models.User.is_valid_user_id(user_id):
        return Response(
            f"Некорректный id пользователя: {user_id}. id должен быть в диапазоне [0, {len(USERS)})",
            status=HTTPStatus.NOT_FOUND)

    user = USERS[user_id]
    response = Response(
        json.dumps(
            {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "total_reactions": user.total_reactions,
                "posts": user.posts,
            }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response
