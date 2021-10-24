from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette import status
from fastapi.responses import JSONResponse
from typing import Optional
from .db import db
from .utils import user_rooms
from .models import CreateNotice
shift = FastAPI()

templates = Jinja2Templates(directory="frontend/")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

shift.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@shift.get("/",status_code=201)
async def root(request: Request):
    return templates.TemplateResponse('index.html',context={'request': request,})

@shift.post("/api/v1/cr",status_code=201)
async def create_shift():
    # print(request)
    return {"done"}




@shift.post("/api/v1/organisation/{org_id}/create",response_model=CreateNotice,status_code=201)
async def create_notice_view(org_id:str,notices:CreateNotice):
        """Create new notices"""
            db.save(
                "noticeboard",
                # "613a1a3b59842c7444fb0220",
                org_id,
                notice_data=notices,
            )

            updated_data = db.read("noticeboard", org_id)

            # created_notice = {
            #     "event":"create_notice",
            #     "data": updated_data
            # }

            user_id = request.GET.get("user")

            update_notice = {
                "event": "sidebar_update",
                "plugin_id": "noticeboard.zuri.chat",
                "data": {
                    "name": "Noticeboard Plugin",
                    "group_name": "Noticeboard",
                    "show_group": False,
                    "button_url": "/noticeboard",
                    "public_rooms": [],
                    "joined_rooms": user_rooms(org_id, user_id),
                },
            }
            db.post_to_centrifugo("team-aquinas-zuri-challenge-007", updated_data)
            db.post_to_centrifugo(f"{org_id}_{user_id}_sidebar", update_notice)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)