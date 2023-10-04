import re
from app import USERS


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

    @staticmethod
    def is_unique_email(email):
        for user in USERS:
            if user.email == email:
                return False
        return True

    @staticmethod
    def is_valid_user_id(user_id):
        if 0 <= user_id < len(USERS):
            return True
