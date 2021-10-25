from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette import status
from fastapi import status, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
import json
from typing import Optional
from starlette.exceptions import HTTPException
from storage.db import db
from utils.utils import user_rooms
from storage.models import CreateNotice,UpdateNotice

app = FastAPI(
    title="Noticeboard API",
    description="Swagger Documentaion For the Noticeboard plugin",
)

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.post(
    "/api/v1/organisation/{org_id}/create",
    response_model=CreateNotice,
    summary="Creates Notices",
    tags=["Notices"],
    status_code=201,
)
async def create_notice_view(org_id: str, notices: CreateNotice):
    """
    This endpoint is used to creates notices for organisations
    """
    notice = notices.dict()

    db.save(
        "noticeboard",
        org_id,
        notice_data=notice,
    )
    updated_data = db.read("noticeboard", org_id)

    # created_notice = {
    #     "event":"create_notice",
    #     "data": updated_data
    # }

    # user_id = request.GET.get("user")

    # update_notice = {
    #     "event": "sidebar_update",
    #     "plugin_id": "noticeboard.zuri.chat",
    #     "data": {
    #         "name": "Noticeboard Plugin",
    #         "group_name": "Noticeboard",
    #         "show_group": False,
    #         "button_url": "/noticeboard",
    #         "public_rooms": [],
    #         "joined_rooms": user_rooms(org_id, user_id),
    #     },
    # }
    # db.post_to_centrifugo("team-aquinas-zuri-challenge-007", updated_data)
    # db.post_to_centrifugo(f"{org_id}_{user_id}_sidebar", update_notice)

    return notice


@app.get(
    "/api/v1/organisation/{org_id}/notices", summary="List of Notices", tags=["Notices"]
)
async def view_notice(org_id: str, response: Response):

    """This endpoint returns all the notices created under a particular
    organisation in the database."""

    # org_id = "613a1a3b59842c7444fb0220"
    notice = db.read("noticeboard", org_id)
    if notice["data"] is not None:
        get_data = notice["data"]
        reversed_list = get_data[::-1]
        # print(reversed_list)
        notice.update(data=reversed_list)
    else:
        notice["data"] = {}
    if notice["status"] == 200:
        print(notice)
        return JSONResponse(notice, status_code=status.HTTP_200_OK)
    return JSONResponse(
        {"status": False, "message": "retrieved unsuccessfully"},
        status_code=status.HTTP_404_NOT_FOUND,
    )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)


@app.delete(
    "/api/v1/organisation/{org_id}/notices/{object_id}/delete",
    summary="Delete Notices",
    tags=["Notices"],
)
def delete_notice(object_id: str, org_id: str, response: Response):
    """Delete a notice from the database."""
    deleted_data = db.delete(
        collection_name="noticeboard", org_id=org_id, object_id=object_id
    )
    data = db.read("noticeboard", org_id)

    db.post_to_centrifugo("team-aquinas-zuri-challenge-007", data)

    if deleted_data["status"] == 200:
        return JSONResponse(
            {"success": True, "message": "Delete Operation Successful"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        {
            "success": False,
            "message": "Delete Operation Failed. Object does not exist in the database",
        },
        status_code=status.HTTP_404_NOT_FOUND,
    )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST)


@app.patch(
    "/api/v1/organisation/{org_id}/notices/{object_id}/edit",
    response_model=UpdateNotice,
    response_model_exclude_none=True,
    summary="Updates Notices",
    tags=["Notices"],
    status_code=201,
)
async def update_notice_view(request: Request,object_id:str, org_id:str,notices: UpdateNotice):
    """Update A Notice In A Database."""

    notice= await request.json()
    print("w"*50)
    print(notice)
    updated=db.update("noticeboard", org_id, notice, object_id=object_id)
    if updated["status"]==200:


        data = db.read("noticeboard", org_id)

        db.post_to_centrifugo("team-aquinas-zuri-challenge-007", data)

        return JSONResponse(
            {
                "success": True,
                "data": notice,
                "message": "Notice has been successfully updated",
            },
            status_code=status.HTTP_201_CREATED,
        )
    return JSONResponse(
    {"success": False, "message": "Notice not updated, Please Try Again"},
    status_code=status.HTTP_400_BAD_REQUEST,)


