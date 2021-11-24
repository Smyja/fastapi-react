from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, constr, AnyUrl,Field
from utils.utils import random_string


class CreateNotice(BaseModel):
    title: constr(max_length=255)
    created: datetime = Field(default_factory=datetime.utcnow)
    author_name: str
    author_username: str
    author_img_url: AnyUrl
    message: str
    media: Optional[List[AnyUrl]] = []
    views: str = 0

class UpdateNotice(BaseModel):
    title: Optional[constr(max_length=255)]
    author_name: Optional[str]
    author_username: Optional[str]
    author_img_url: Optional[AnyUrl]
    message: Optional[str]
    media: Optional[List[AnyUrl]] = []
    views: Optional[str] 
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

class NoticeboardRoom(BaseModel):
    room_id: str = random_string()
    is_admin: Optional[str] = None
    room_name: str
    private = bool = False
    room_member_id: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InstallPlugin(BaseModel):
    organisation_id: str
    user_id: str

class UninstallPlugin(BaseModel):
    organisation_id: str
    user_id: str

class BookmarkNotice(BaseModel):
    notice_id: str
    user_id: str

class NoticeDraft(BaseModel):
    title: constr(max_length=255)
    time: datetime
    date: datetime