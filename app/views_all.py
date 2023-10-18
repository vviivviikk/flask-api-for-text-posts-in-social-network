from app import app, USERS, POSTS
from flask import url_for
import matplotlib
import matplotlib.pyplot as plt
import os


@app.get("/")
def init():
    response = (
        f"<h1>Flask project for social media platform!</h1>"
        f"<b>USERS:</b><br><i>{'<br>'.join([user.repr() for user in USERS])}</i><br><br>"
        f"<b>POSTS:</b><br><i>{'<br>'.join([post.repr() for post in POSTS])}</i><br>"
    )
    matplotlib.use("Agg")

    user_names = [user.get_partial_user_data() for user in USERS]
    user_reactions = [user.get_total_reactions() for user in USERS]

    bar_color = "green"

    plt.bar(user_names, user_reactions, color=bar_color)
    plt.ylabel("Number of user reactions")
    plt.xlabel("User name, last name, id")
    plt.title("Bar chart of users by number of reactions")
    plt.savefig(os.path.join("app", "static", "leaderboard.png"))

    response += f'<img src="{url_for("static", filename="leaderboard.png")}">'

    return response
