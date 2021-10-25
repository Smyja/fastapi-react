from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, constr, AnyUrl,Field


class CreateNotice(BaseModel):
    title: constr(max_length=255)
    created: datetime = Field(default_factory=datetime.utcnow)
    author_name: str
    author_username: str
    author_img_url: AnyUrl
    message: str
    media: Optional[List[AnyUrl]] = []
    views: str = 0

# a=CreateNotice(
#   title= "string",
#   created="2019-08-24T14:15:22Z",
#   author_name= "string",
#   author_username= "string",
#   author_img_url= "http://example.com",
#   message= "string",
#   media= [],
#   views= 0
# )
# print(a.json())