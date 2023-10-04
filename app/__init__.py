from flask import Flask

app = Flask(__name__)  # name __init__

USERS = []  # global variable (list objects of type User)

from app import views
from app import models
