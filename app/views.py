from app import app, USERS, models, POSTS
from flask import request, Response, url_for
import json
from http import HTTPStatus
from operator import itemgetter
import matplotlib
import matplotlib.pyplot as plt


@app.get("/")
def init():
    response = (
        f"<h1>Flask project for social media platform!</h1>"
        f"<b>USERS:</b><br><i>{'<br>'.join([user.repr() for user in USERS])}</i><br><br>"
        f"<b>POSTS:</b><br><i>{'<br>'.join([post.repr() for post in POSTS])}</i><br>"
    )
    return response


@app.route("/users/create", methods=["POST"])
def user_create():
    data = request.get_json()
    user_id = len(USERS)
    first_name = data["first_name"]
    last_name = data["last_name"]
    email = data["email"]

    if not models.User.is_valid_name(first_name, last_name):
        return Response(
            f"Вы ввели некорректное имя '{first_name}' или фамилию '{last_name}'",
            status=HTTPStatus.BAD_REQUEST,
        )

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
            f"Некорректный id пользователя: {user_id}, id должен быть в диапазоне [0, {len(USERS)})",
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

    if leaderboard_type not in ["list", "graph"]:
        return Response(
            f"Неверный тип запроса '{leaderboard_type}', допустимые типы: 'list' / 'graph'",
            status=HTTPStatus.BAD_REQUEST,
        )

    if leaderboard_type == "list":
        sort_type = data["sort"]
        if sort_type not in ["asc", "desc"]:
            return Response(
                f"Введен неправильный тип сортировки '{sort_type}', допустимые типы: 'asc' / 'desc'",
                status=HTTPStatus.BAD_REQUEST,
            )

        sorted_users = sorted(USERS, reverse=(sort_type == "desc"))
        leaderboard = list(map(lambda user: user.convert_to_dict(), sorted_users))

        return Response(
            json.dumps({"users": leaderboard}),
            status=HTTPStatus.OK,
            mimetype="application/json",
        )

    elif leaderboard_type == "graph":
        if "sort" in data:
            return Response(
                "Поле 'sort' в данном запросе не должно быть",
                status=HTTPStatus.BAD_REQUEST,
            )

        matplotlib.use("Agg")

        user_names = [user.get_partial_user_data() for user in USERS]
        user_reactions = [user.get_total_reactions() for user in USERS]

        bar_color = "green"

        plt.bar(user_names, user_reactions, color=bar_color)
        plt.ylabel("Реакции пользователей")
        plt.title("График пользователей по количеству реакций")
        plt.savefig("app/users_graph.png")

        return Response(
            f"""<img src = "{url_for('static', filename='leaderboard.png')}">""",
            status=HTTPStatus.OK,
            mimetype="text/html",
        )
