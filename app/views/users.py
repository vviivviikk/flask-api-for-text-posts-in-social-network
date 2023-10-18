from app import app, USERS, models, POSTS
from flask import request, Response, url_for
import json
from http import HTTPStatus
from operator import itemgetter
import matplotlib
import matplotlib.pyplot as plt


@app.route("/users/create", methods=["POST"])
def user_create():
    try:
        if request.headers.get("Content-Type") != "application/json":
            return Response(
                "Invalid content type. Content type should be application/json",
                status=HTTPStatus.BAD_REQUEST,
            )

        data = request.get_json()
        user_id = len(USERS)
        first_name = data["first_name"]
        last_name = data["last_name"]
        email = data["email"]

        if not models.User.is_valid_name(first_name, last_name):
            return Response(
                f"You entered an invalid name '{first_name}' or last name '{last_name}'",
                status=HTTPStatus.BAD_REQUEST,
            )

        if not models.User.is_valid_email(email):
            return Response(
                f"You entered an invalid email: '{email}'",
                status=HTTPStatus.BAD_REQUEST,
            )
        if not models.User.is_unique_email(email):
            return Response(
                f"Email '{email}' is already used by another user",
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
    except KeyError as e:
        return Response(
            f"Missing required key in input data: {str(e)}",
            status=HTTPStatus.BAD_REQUEST,
        )


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    if not str(user_id).isdigit():
        return Response(
            f"Invalid user_id: {user_id}, user_id should be an integer",
            status=HTTPStatus.BAD_REQUEST,
        )

    user_id = int(user_id)

    if not models.User.is_valid_user_id(user_id):
        return Response(
            f"Invalid user_id: {user_id}, user_id should be in range [0, {len(USERS)})",
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


@app.route("/users/<user_id>/posts", methods=["GET"])
def get_all_posts(user_id):
    if not str(user_id).isdigit():
        return Response(
            f"Invalid user_id: {user_id}, user_id should be an integer",
            status=HTTPStatus.BAD_REQUEST,
        )

    user_id = int(user_id)

    try:
        if request.headers.get("Content-Type") != "application/json":
            return Response(
                "Invalid content type. Content type should be application/json",
                status=HTTPStatus.BAD_REQUEST,
            )
        data = request.get_json()
        sort_type = data["sort"]

        if not models.User.is_valid_user_id(user_id):
            return Response(
                f"Invalid user_id: {user_id}. user_id should be in range [0, {len(USERS)})",
                status=HTTPStatus.NOT_FOUND,
            )

        all_posts = {
            post_num: POSTS[post_num].get_reactions_count()
            for post_num in USERS[user_id].get_all_posts()
        }

        if sort_type == "asc":
            sorted_posts = dict(sorted(all_posts.items(), key=itemgetter(1)))
        elif sort_type == "desc":
            sorted_posts = dict(
                sorted(all_posts.items(), key=itemgetter(1), reverse=True)
            )
        else:
            return Response(
                f"Invalid sort type {sort_type}, allowed types: 'asc' or 'desc'",
                status=HTTPStatus.BAD_REQUEST,
            )

        posts = [POSTS[post_id].convert_to_dict() for post_id in sorted_posts.keys()]

        response = Response(
            json.dumps({"posts": posts}),
            HTTPStatus.OK,
            mimetype="application/json",
        )
        return response
    except KeyError as e:
        return Response(
            f"Missing required key in input data: {str(e)}",
            status=HTTPStatus.BAD_REQUEST,
        )


@app.route("/users/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        if request.headers.get("Content-Type") != "application/json":
            return Response(
                "Invalid content type. Content type should be application/json",
                status=HTTPStatus.BAD_REQUEST,
            )
        data = request.get_json()
        leaderboard_type = data["type"]

        if leaderboard_type not in ["list", "graph"]:
            return Response(
                f"Invalid leaderboard type '{leaderboard_type}', allowed types: 'list' or 'graph'",
                status=HTTPStatus.BAD_REQUEST,
            )

        if leaderboard_type == "list":
            sort_type = data["sort"]
            if sort_type not in ["asc", "desc"]:
                return Response(
                    f"Invalid sort type '{sort_type}', allowed types: 'asc' or 'desc'",
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
                    "Field 'sort' should not be present in this request",
                    status=HTTPStatus.BAD_REQUEST,
                )

            matplotlib.use("Agg")

            user_names = [user.get_partial_user_data() for user in USERS]
            user_reactions = [user.get_total_reactions() for user in USERS]

            bar_color = "green"

            plt.bar(user_names, user_reactions, color=bar_color)
            plt.ylabel("Number of user reactions")
            plt.xlabel("User name, last name, id")
            plt.title("Bar chart of users by number of reactions")
            plt.savefig("app/static/leaderboard.png")

            return Response(
                f"""<img src = "{url_for('static', filename='leaderboard.png')}">""",
                status=HTTPStatus.OK,
                mimetype="text/html",
            )
    except KeyError as e:
        return Response(
            f"Missing required key in input data: {str(e)}",
            status=HTTPStatus.BAD_REQUEST,
        )
