from app import app, USERS, models, POSTS
from flask import request, Response
import json
from http import HTTPStatus


@app.route("/posts/create", methods=["POST"])
def post_create():
    try:
        if request.headers.get("Content-Type") != "application/json":
            return Response(
                "Invalid content type. Content type should be application/json",
                status=HTTPStatus.BAD_REQUEST,
            )
        data = request.get_json()
        post_id = len(POSTS)
        author_id = data["author_id"]
        text = data["text"]

        if not models.Post.is_valid_author_id(author_id):
            return Response(
                f"Invalid author id: {type(author_id)}, id should be an integer",
                status=HTTPStatus.BAD_REQUEST,
            )

        if not models.User.is_valid_user_id(author_id):
            return Response(
                f"Invalid author id: {author_id}, id should be in range [0, {len(USERS)})",
                status=HTTPStatus.NOT_FOUND,
            )

        if not models.Post.is_valid_post_text(text):
            return Response(
                f"Invalid text type: {type(text)}. Text in the post should be of type string",
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
    except KeyError as e:
        return Response(
            f"Missing required key in input data: {str(e)}",
            status=HTTPStatus.BAD_REQUEST,
        )


@app.route("/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    if not str(post_id).isdigit():
        return Response(
            f"Invalid post_id: '{post_id}', post_id should be an integer",
            status=HTTPStatus.BAD_REQUEST,
        )

    post_id = int(post_id)

    if not models.Post.is_valid_post_id(post_id):
        return Response(
            f"Invalid post_id: {post_id}, post_id should be in range [0, {len(POSTS)})",
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


@app.route("/posts/<post_id>/reaction", methods=["POST"])
def post_reaction(post_id):
    if not str(post_id).isdigit():
        return Response(
            f"Invalid post_id: '{post_id}', post_id should be an integer",
            status=HTTPStatus.BAD_REQUEST,
        )

    post_id = int(post_id)

    try:
        if request.headers.get("Content-Type") != "application/json":
            return Response(
                "Invalid content type. Content type should be application/json",
                status=HTTPStatus.BAD_REQUEST,
            )
        data = request.get_json()
        user_id = data["user_id"]
        reaction = data["reaction"]

        if not models.Post.is_valid_post_id(post_id):
            return Response(
                f"Invalid user post_id: {post_id}. post_id should be in range [0, {len(POSTS)})",
                status=HTTPStatus.NOT_FOUND,
            )

        if not models.Post.is_valid_author_id(user_id):
            return Response(
                f"Invalid user id type: {type(user_id)}. id should be an integer",
                status=HTTPStatus.BAD_REQUEST,
            )

        if not models.User.is_valid_user_id(user_id):
            return Response(
                f"Invalid author id: {user_id}, id should be in range [0, {len(USERS)})",
                status=HTTPStatus.NOT_FOUND,
            )

        if models.Post.yourself_post_reaction(user_id, post_id):
            return Response(
                f"You cannot react to your own post",
                status=HTTPStatus.BAD_REQUEST,
            )

        if not models.Post.is_valid_reaction(reaction):
            return Response(
                f"Invalid reaction, allowed reactions: 'heart', 'like', 'dislike', 'boom', 'fire', 'party'",
                status=HTTPStatus.BAD_REQUEST,
            )

        user = USERS[user_id]
        post = POSTS[post_id]

        if user_id in post.reaction_users and reaction in post.reaction_users[user_id]:
            return Response(
                f"You have already reacted with {reaction} to this post",
                status=HTTPStatus.BAD_REQUEST,
            )

        user.increase_reactions()
        post.reactions.append(reaction)

        post.reaction_users.setdefault(user_id, []).append(reaction)

        return Response(status=HTTPStatus.OK)
    except KeyError as e:
        return Response(
            f"Missing required key in input data: {str(e)}",
            status=HTTPStatus.BAD_REQUEST,
        )
