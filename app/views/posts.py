from app import app, USERS, models, POSTS
from flask import request, Response
import json
from http import HTTPStatus


@app.route("/posts/create", methods=["POST"])
def post_create():
    data = request.get_json()
    post_id = len(POSTS)
    author_id = data["author_id"]
    text = data["text"]

    if not models.Post.is_valid_author_id(author_id):
        return Response(
            f"Некорректный id автора: {type(author_id)}, id должен быть целым числом",
            status=HTTPStatus.BAD_REQUEST,
        )

    if not models.User.is_valid_user_id(author_id):
        return Response(
            f"Некорректный id автора: {author_id}, id должен быть в диапазоне [0, {len(USERS)})",
            status=HTTPStatus.NOT_FOUND,
        )

    if not models.Post.is_valid_post_text(text):
        return Response(
            f"Некорректный тип текста: {type(text)}. Текст в посте должен быть строкой",
            status=HTTPStatus.BAD_REQUEST,
        )

    post = models.Post(post_id, author_id, text)
    POSTS.append(post)
    USERS[author_id].add_new_post(post_id)
    response = Response(
        json.dumps(
            {
                "id": post.post_id,
                "author_id": post.author_id,
                "text": post.text,
                "reactions": post.reactions,
            }
        ),
        HTTPStatus.CREATED,
        mimetype="application/json",
    )
    return response


@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    if not models.Post.is_valid_post_id(post_id):
        return Response(
            f"Некорректный post_id: {post_id}, post_id должен быть в диапазоне [0, {len(POSTS)})",
            status=HTTPStatus.NOT_FOUND,
        )

    post = POSTS[post_id]
    response = Response(
        json.dumps(
            {
                "id": post.post_id,
                "author_id": post.author_id,
                "text": post.text,
                "reactions": post.reactions,
            }
        ),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@app.route("/posts/<int:post_id>/reaction", methods=["POST"])
def post_reaction(post_id):
    data = request.get_json()
    user_id = data["user_id"]
    reaction = data["reaction"]

    if not models.Post.is_valid_post_id(post_id):
        return Response(
            f"Некорректный post_id пользователя: {post_id}. post_id должен быть в диапазоне [0, {len(POSTS)})",
            status=HTTPStatus.NOT_FOUND,
        )

    if not models.Post.is_valid_author_id(user_id):
        return Response(
            f"Некорректный тип id пользователя: {type(user_id)}. id должен быть целым числом",
            status=HTTPStatus.BAD_REQUEST,
        )

    if not models.User.is_valid_user_id(user_id):
        return Response(
            f"Некорректный id автора: {user_id}, id должен быть в диапазоне [0, {len(USERS)})",
            status=HTTPStatus.NOT_FOUND,
        )

    if models.Post.yourself_post_reaction(user_id, post_id):
        return Response(
            f"Вы не можете поставить реакцию на свой пост",
            status=HTTPStatus.BAD_REQUEST,
        )

    if not models.Post.is_valid_reaction(reaction):
        return Response(
            f"Некорректная реакция, список разрешенных реакций: 'heart', 'like', 'dislike', 'boom', 'fire', 'party'",
            status=HTTPStatus.BAD_REQUEST,
        )

    user = USERS[user_id]
    post = POSTS[post_id]

    if user_id in post.reaction_users and reaction in post.reaction_users[user_id]:
        return Response(
            f"Вы уже поставили реакцию {reaction} на этот пост",
            status=HTTPStatus.BAD_REQUEST,
        )

    user.increase_reactions()
    post.reactions.append(reaction)

    post.reaction_users.setdefault(user_id, []).append(reaction)

    return Response(status=HTTPStatus.OK)
