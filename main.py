from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from typing import Optional
from .db import db
from .utils import user_rooms
from .models import CreateNotice

app = FastAPI()

templates = Jinja2Templates(directory="frontend/")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=201)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
        },
    )


@app.post("/api/v1/cr", status_code=201)
async def create_shift():
    # print(request)
    return {"done"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.post(
    "/api/v1/organisation/{org_id}/create", response_model=CreateNotice, status_code=201
)
async def create_notice_view(org_id: str, notices: CreateNotice):
    db.save(
        "noticeboard",
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

    return notices
