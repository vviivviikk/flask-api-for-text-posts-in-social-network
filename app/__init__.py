from flask import Flask

app = Flask(__name__)  # name __init__

USERS = []  # list objects of type User
POSTS = []  # list objects of type Post
ALLOWED_REACTIONS = [
    "heart",
    "like",
    "dislike",
    "boom",
    "fire",
    "party",
]  # list allowed reaction for post

from app import views
from app import models
