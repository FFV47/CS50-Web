import json
from pydantic import BaseModel, ValidationError


class EditPost(BaseModel):
    post_id: int
    text: str


class LikePost(BaseModel):
    post_id: int


class NewPost(BaseModel):
    post_text: str


class NewComment(BaseModel):
    comment_text: str
    post_id: int
    parent_comment_id: int | None = None


class GetUsername(BaseModel):
    username: str = ""


if __name__ == "__main__":
    external_data = b'{"post_id": 1, "text": "Nova postagem"}'
    external_data = b'{"text": "Nova postagem", "post_id": 2}'

    try:
        data = EditPost.parse_raw(external_data).dict()
    except ValidationError as e:
        message = ", ".join(
            [f"{error['loc']}: {error['msg']}" for error in json.loads(e.json())]
        )
        print(message)
        exit(1)

    print(data)
