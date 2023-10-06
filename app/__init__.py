from flask import Flask

app = Flask(__name__)  # name __init__

USERS = []  # list objects of type User
POSTS = []  # list objects of type Post

from app import views
from app import models
