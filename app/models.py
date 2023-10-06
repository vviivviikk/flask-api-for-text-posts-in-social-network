import re
from app import USERS, POSTS


class User:
    def __init__(
        self, user_id, first_name, last_name, email, total_reactions=0, posts=None
    ):
        if posts is None:
            posts = []
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.total_reactions = total_reactions
        self.posts = posts

    @staticmethod
    def is_valid_email(email):
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return True
        return False

    @staticmethod
    def is_unique_email(email):
        for user in USERS:
            if user.email == email:
                return False
        return True

    @staticmethod
    def is_valid_user_id(user_id):
        return 0 <= user_id < len(USERS)

    def add_new_post(self, post):
        self.posts.append(post)


class Post:
    def __init__(self, post_id, author_id, text, reactions=None):
        if reactions is None:
            reactions = []
        self.post_id = post_id
        self.author_id = author_id
        self.text = text
        self.reactions = reactions

    @staticmethod
    def is_valid_post_id(post_id):
        if 0 <= post_id < len(POSTS):
            return True

    @staticmethod
    def yourself_post_reaction(user_id, post_id):
        return user_id == POSTS[post_id].author_id
