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

    def increase_reactions(self):
        self.total_reactions += 1

    def get_all_posts(self):
        return self.posts

    def convert_to_dict(self):
        return {
            "id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "total_reactions": self.total_reactions,
        }

    def get_partial_user_data(self):
        return f"{self.first_name} {self.last_name} ({self.user_id})"

    def get_total_reactions(self):
        return self.total_reactions

    def __lt__(self, other):
        return self.total_reactions < other.total_reactions


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

    def get_reactions_count(self):
        return len(self.reactions)

    def convert_to_dict(self):
        return {
            "post_id": self.post_id,
            "author_id": self.author_id,
            "text": self.text,
            "reactions": self.reactions,
        }
