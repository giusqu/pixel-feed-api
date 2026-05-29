from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserPostIn(BaseModel):  # data coming in the API from the client
    """Create the structure of a new user post"""

    body: str


class UserPost(UserPostIn):  # data going out to the client
    """Inherits from UserPostIn and adds an id"""

    id: int
    user_id: int
    image_url: Optional[str] = None

    # ConfigDict(from_attributes=True)
    # ORM mode (to access an object's attributes using dot notation)
    # pydantic first tries to access the value like a dictionary (value["body"])
    # if that fails, it then tries to access it as an object attribute (value.body)
    model_config = ConfigDict(from_attributes=True)  # pydantic 2.0

    # class Config: # pydantic 1.0
    #     orm_mode = True


class UserPostWithLikes(UserPost):
    likes: int

    model_config = ConfigDict(from_attributes=True)


class CommentIn(BaseModel):
    """Creates the structure of a new comment"""

    body: str
    post_id: int


class Comment(CommentIn):
    """Inherits from CommentIn and adds an id"""

    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserPostWithComments(BaseModel):
    """Usa UserPost e Comment (list)
    {
        "post": {"id": 0, "body": "My post", "likes": 0},
        "comments": [{"id": 2,"post_id": 0, "body": "My comment"}]
    }
    """

    post: UserPostWithLikes
    comments: list[Comment]


class PostLikeIn(BaseModel):
    post_id: int


class PostLike(PostLikeIn):
    id: int
    user_id: int
