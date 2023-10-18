# Flask project for social media platform

A full-fledged service needs to be created that performs the following functions:

+ Creates a user (checks the email for correctness) who can write posts and react (heart, like, dislike, boom, ...) to posts from other users
+ Provides data on a specific user
+ Creates a post
+ Provides data on a specific post
+ User reacts to a post
+ Provides all posts of a user, sorted by the number of reactions
+ Generates a list of users sorted by the number of reactions
+ Generates a graph of users based on the number of reactions

Assumptions:

- Objects are allowed to be stored in runtime
- Email validation can be done through regular expressions, third-party libraries

Required:

- Code must be properly formatted (e.g., using black)
- Handle all edge cases (user does not exist, user with such email is already registered, etc.)

# Requests and responses

- Create a user `POST /users/create`

Request example:
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string"
}
```

Response example:
```json
{
  "id": "number",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "total_reactions": "number",
  "posts": []
}
```

- Get data on a specific user `GET /users/<user_id>`

Response example:
```json
{
  "id": "number",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "total_reactions": "number",
  "posts": [
    "number",
    ...
  ]
}
```

- Create a post `POST /posts/create`

Request example:
```json
{
  "author_id": "number",
  "text": "string"
}
```

Response example:
```json
{
  "id": "number",
  "author_id": "number",
  "text": "string",
  "reactions": [
  	"string",
    ...
  ] 
}
```

- Get data on a specific post `GET /posts/<post_id>`

Response example:
```json
{
  "id": "number",
  "author_id": "number",
  "text": "string",
  "reactions": [
  	"string",
    ...
  ] 
}
```

- React to a post `POST /posts/<post_id>/reaction`

Request example:
```json
{
  "user_id": "number",
  "reaction": "string"
}
```

Response example: (Empty, only response code)

- Get all posts of a user, sorted by the number of reactions `GET /users/<user_id>/posts`

The value `asc` denotes `ascending`, the `desc` parameter denotes `descending`

Request example:
```json
{
  "sort": "asc/desc"
}
```

Response example:
```json
{
	"posts": [
    	{
  			"id": "number",
  			"author_id": "string",
  			"text": "string",
  			"reactions": [
  				"string",
    			...
  			] 
  		},
        {
        	...
        }
    ]
}
```

- Get all users, sorted by the number of reactions `GET /users/leaderboard`

The value `asc` denotes `ascending`, the `desc` parameter denotes `descending`

Request example:
```json
{
  "type": "list",
  "sort": "asc/desc"
}
```

Response example:
```json
{
	"users": [
    	{
          "id": "number",
          "first_name": "string",
          "last_name": "string",
          "email": "string",
          "total_reactions": "number"
		},
        {
        	...
        }
    ]
}
```

- Get a graph of users based on the number of reactions `GET /users/leaderboard`

Request example:
```json
{
  "type": "graph"
}
```

Response example:
```html
<img src="path_to_graph">
```