from app import app, USERS, models, POSTS
from flask import request, Response, url_for
import json
from http import HTTPStatus
from operator import itemgetter
from matplotlib import pyplot as plt


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
            status=HTTPStatus.NOT_FOUND,
        )

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


@app.route("/posts/create", methods=["POST"])
def post_create():
    data = request.get_json()
    post_id = len(POSTS)
    author_id = data["author_id"]
    text = data["text"]

    if not models.User.is_valid_user_id(author_id):
        return Response(
            f"Некорректный id автора:",
            status=HTTPStatus.NOT_FOUND,
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
            f"Некорректный post_id пользователя: {post_id}. post_id должен быть в диапазоне [0, {len(POSTS)})",
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

    if not models.User.is_valid_user_id(user_id) or not models.Post.is_valid_post_id(
        post_id
    ):
        return Response(
            f"Некорректный user_id: {user_id} или post_id: {post_id}",
            status=HTTPStatus.NOT_FOUND,
        )

    if models.Post.yourself_post_reaction(user_id, post_id):
        return Response(
            f"Вы не можете поставить реакцию на свой пост",
            status=HTTPStatus.BAD_REQUEST,
        )

    user = USERS[user_id]
    post = POSTS[post_id]

    user.increase_reactions()
    post.reactions.append(reaction)

    return Response(status=HTTPStatus.OK)


@app.route("/users/<int:user_id>/posts", methods=["GET"])
def get_all_posts(user_id):
    data = request.get_json()
    sort_type = data["sort"]

    if not models.User.is_valid_user_id(user_id):
        return Response(
            f"Некорректный id пользователя: {user_id}. id должен быть в диапазоне [0, {len(USERS)})",
            status=HTTPStatus.NOT_FOUND,
        )

    all_posts = {
        post_num: POSTS[post_num].get_reactions_count()
        for post_num in USERS[user_id].get_all_posts()
    }

    if sort_type == "asc":
        sorted_posts = dict(sorted(all_posts.items(), key=itemgetter(1)))
    elif sort_type == "desc":
        sorted_posts = dict(sorted(all_posts.items(), key=itemgetter(1), reverse=True))
    else:
        return Response(
            f"Введен неправильный тип сортировки {sort_type}, допустимые типы: asc / desc",
            status=HTTPStatus.BAD_REQUEST,
        )

    posts = [POSTS[post_id].convert_to_dict() for post_id in sorted_posts.keys()]

    response = Response(
        json.dumps({"posts": posts}),
        HTTPStatus.OK,
        mimetype="application/json",
    )
    return response


@app.route("/users/leaderboard", methods=["GET"])
def get_leaderboard():
    data = request.get_json()
    leaderboard_type = data["type"]

    if leaderboard_type == "list":
        sort_type = data["sort"]
        if sort_type not in ["asc", "desc"]:
            return Response(
                f"Введен неправильный тип сортировки {sort_type}, допустимые типы: asc / desc",
                status=HTTPStatus.BAD_REQUEST,
            )

        sorted_users = sorted(USERS, reverse=(sort_type == "desc"))
        leaderboard = list(map(lambda user: user.convert_to_dict(), sorted_users))

        return Response(
            json.dumps({"users": leaderboard}),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )

    if leaderboard_type == "graph":
        user_names = [user.get_partial_user_data() for user in USERS]
        user_reactions = [user.get_total_reactions() for user in USERS]
        plt.bar(user_names, user_reactions)
        plt.ylabel("Реакции пользователей")
        plt.title("График пользователей по количеству реакций")
        plt.savefig("app/users_graph.png")

        return Response(
            f"""<img src = "{url_for('static', filename='leaderboard.png')}">""",
            status=HTTPStatus.OK,
            mimetype="text/html",
        )
