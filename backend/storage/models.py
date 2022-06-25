from datetime import datetime,  date
from typing import List, Optional
from pydantic import BaseModel, constr, AnyUrl,Field,ValidationError, validator
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

    date: date

class EmailSubscribe(BaseModel):
    email: str

class AddMemberToRoom(BaseModel):
    room_id: constr(max_length=50)
    member_ids: List[constr(max_length=50)]

class ScheduleNotice(BaseModel):
    title: constr(max_length=255)
    created: datetime = Field(default_factory=datetime.utcnow)
    author_name: str
    author_username: str
    author_img_url: AnyUrl
    message: str
    media: Optional[List[AnyUrl]] = []
    views: str = 0
    timer: datetime 
    
    @validator('timer')
    def validate_timer(cls,value):
        if datetime.now() > value.replace(tzinfo=None):
            print(datetime.now())
            print(value.replace(tzinfo=None))
            raise ValueError('Date cannot be in the past')
        return value

