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
from storage.models import *
import requests

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

settings_PLUGIN_ID = "61694eea9ea5d3be97df2973"

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


@app.get(
    "/api/v1/sidebar",
    summary="Returns Sidebar Data",
    tags=["Sidebar"],
)
def sidebar_info(org_id: str, user_id: str):
    """Returns the room the logged in user belongs to under Noticeboard
    plugin"""
    # org_id = request.GET.get("org")
    # user_id = request.GET.get("user")

    if org_id and user_id:
        sidebar = {
            "name": "Noticeboard Plugin",
            "description": "Displays Information On A Noticeboard",
            "plugin_id": settings_PLUGIN_ID,
            "organisation_id": f"{org_id}",
            "user_id": f"{user_id}",
            "category": "productivity",
            "group_name": "Noticeboard",
            "show_group": False,
            "public_rooms": [],
            "joined_rooms": user_rooms(org_id, user_id),
        }
        return JSONResponse(sidebar)
    return JSONResponse(
        {"message": "org id or user id is None"}, status_code=status.HTTP_400_BAD_REQUEST
    )

# def create_plugin_room(org_id, user_id):
#     """Function that creates a Noticeboard room"""
#     room = db.read("noticeboard_room", org_id)
#     if room["status"] == 200:
#         if room["data"] is not None:
#             room = room["data"][0]
#         else:
#             serializer = NoticeboardRoom(data={"room_name": "Noticeboard"})
#             if serializer.is_valid():
#                 room = serializer.data
#                 room.update({"is_admin": user_id})
#                 if user_id not in room["room_member_id"]:
#                     room.update({"room_member_id": [user_id]})
#                     db.save("noticeboard_room", org_id, notice_data=room)


@app.post(
    "/api/v1/install",
    tags=["Install"],
    summary="Install Noticeboard Plugin",
    status_code=200,
)
# async def install_plugin(request: Request, install: InstallPlugin, notice_room: NoticeboardRoom(room_name="Noticeboard")):
async def install_plugin(request: Request, install: InstallPlugin):
    """This endpoint is called when an organisation wants to install the
    Noticeboard plugin for their workspace."""

    serializer = install.dict()
    nHeaders = request.headers["Authorization"]
    
    install_payload = serializer
    org_id = install_payload["organisation_id"]
    user_id = install_payload["user_id"]
    print(org_id, user_id)

        # new_token = db.token()
        # print(new_token)

    url = f"https://api.zuri.chat/organizations/{org_id}/plugins"
    print(url)
    payload = {"plugin_id": settings_PLUGIN_ID, "user_id": user_id}
    v2load = json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"{nHeaders}"}
    print(headers)
    response = requests.request("POST", url, headers=headers, data=v2load)
    installed = json.loads(response.text)
    print(installed)
    if installed["status"] == 200:

        # room = db.read("noticeboard_room", org_id)
        # if room["status"] == 200:
        #     if room["data"] is not None:
        #         room = room["data"][0]
        #     else:
        #         room = notice_room.dict()
        #         room.update({"is_admin": user_id})
        #         if user_id not in room["room_member_id"]:
        #             room.update({"room_member_id": [user_id]})
        #             db.save("noticeboard_room", org_id, notice_data=room)

        return JSONResponse(
            {
                "success": True,
                "data": {"redirect_url": "/noticeboard"},
                "message": "sucessfully retrieved",
            }
        )
    return JSONResponse(
        {
            "success":False,
            "message":"Plugin has already been added",
        }
    )


@app.delete(
    "/api/v1/uninstall",
    summary="Uninstall Noticeboard Plugin",
    tags=["Uninstall"],
)
def uninstall_plugin(uninstall: UninstallPlugin):
    """This endpoint is called when an organisation wants to uinstall the
    Noticeboard plugin for their workspace."""
    serializer = uninstall.dict()
    uninstall_payload = serializer
    org_id = uninstall_payload["organisation_id"]
    user_id = uninstall_payload["user_id"]
    print(user_id)

    new_token = db.token()
    print(new_token)

    url = (
        f"https://api.zuri.chat/organizations/{org_id}/plugins/{settings_PLUGIN_ID}"
    )
    print(url)
    payload = {"user_id": user_id}
    v2load = json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {new_token}"}
    response = requests.request("DELETE", url, headers=headers, data=v2load)
    uninstalled = json.loads(response.text)
    print(uninstalled)
    if uninstalled["status"] == 200:
        return JSONResponse(
            uninstalled,
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        {"message": "Plugin does not exist"}, status_code=status.HTTP_404_NOT_FOUND
    )

@app.post(
    "/api/v1/organisation/{org_id}/user/{user_id}/room",
    tags=["Room"],
    summary="Create Noticeboard Room",
)
async def create_noticeboard_room(org_id: str, user_id: str, notice_room: NoticeboardRoom):
    """Creates a room for the organisation under Noticeboard plugin."""
    # org_id = "6145b49e285e4a18402073bc"
    # org_id = "614679ee1a5607b13c00bcb7"
    room = db.read("noticeboard_room", org_id)
    if room["status"] == 200:
        if room["data"] is not None:
            room = room["data"][0]
            return JSONResponse(
                {"message": "room already exists", "data": room}, status_code=status.HTTP_200_OK
            )
        else:
            serializer = jsonable_encoder(notice_room)
            room = serializer
            room.update({"is_admin": user_id})
            if user_id not in room["room_member_id"]:
                room.update({"room_member_id": [user_id]})
                db.save("noticeboard_room", org_id, notice_data=room)
            return JSONResponse(
                {"message": "successfully created your room", "data": room},
                status_code=status.HTTP_201_CREATED,
            )
    return JSONResponse(
        {"message": "room couldn't be created"},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

@app.get(
    "/api/v1/organisation/{org_id}/get-room",
    tags=["Room"],
    summary="List Noticeboard Room",
    status_code=200,
)
def get_room(org_id: str):
    """Gets all the rooms created under the Noticeboard plugin."""
    # org_id = "613a1a3b59842c7444fb0220"
    # org_id = "6145b49e285e4a18402073bc"
    # org_id = "614679ee1a5607b13c00bcb7"
    data = db.read("noticeboard_room", org_id)
    if data["data"] is None:
        data["data"] = {}
    return JSONResponse(data)

@app.delete(
    "/api/v1/organisation/{org_id}/room/{obj_id}/delete",
    tags=["Room"],
    summary="Delete Noticeboard Room",
)
def delete_room(org_id: str, obj_id: str):
    """This endpoint enables a user delete a room."""
    deleted_room = db.delete(org_id, "noticeboard_room", obj_id)

    if deleted_room["status"] == 200:
        return JSONResponse(
            {"message": "successfully deleted room"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        {"message": "could not delete room"},
        status_code=status.HTTP_404_NOT_FOUND,
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

    return JSONResponse({
        "success":True,
        "data":notice,
        "message":"successfully created"
    })


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

    notice= notices.dict(exclude_unset=True)
    #61767acbbc003777d000a92a

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

@app.get(
    "/api/v1/organisation/{org_id}/user/{user_id}/bookmark",
    summary="List Bookmarked Notices",
    tags=["Bookmark"],
)
def bookmark_notice(org_id: str, user_id: str):
    """Retrieve all the notices a particular user has bookmarked."""
    bookmarked_notices = db.read(
        "bookmark_notice", org_id, filter={"user_id": user_id}
    )
    if bookmarked_notices["status"] == 200:
        return JSONResponse(
            {
                "success":True,
                "data":bookmarked_notices["data"] or {},
                "message":"Notices successfully retrieved"
            }, 
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        {
            "success":False,
            "message": "Notice does not exist"
        }, 
        status_code=status.HTTP_404_NOT_FOUND
    )

@app.post(
    "/api/v1/organisation/{org_id}/bookmark",
    tags=["Bookmark"],
    summary="Bookmark A Notice",
    status_code=201,
)
def create_bookmark(org_id: str, notice: BookmarkNotice):
    """This endpoint enables a user to bookmark a notice."""
    serializer = notice.dict()

    # bookmark_data = {
    #     "user_id":serializer.data["user_id"],
    #     "notice_data":notice["data"]
    # }

    bookmarked_data = db.save("bookmark_notice", org_id, serializer)

    # response = requests.get(f"https://noticeboard.zuri.chat/api/v1/organisation/{org_id}/get-room")
    # room = response.json()
    # room_id = room["data"][0]["_id"]

    # notice = db.read('noticeboard',org_id, filter={"_id":serializer.data["notice_id"]})

    # data = {
    #     "event":"create_bookmark",
    #     "data":notice["data"]
    # }

    # db.post_to_centrifugo("team-aquinas-zuri-challenge-007", data)
    db.post_to_centrifugo("team-aquinas-zuri-challenge-007", bookmarked_data)

    return JSONResponse({
        "success":True,
        "data":serializer,
        "message":"successfully bookmarked"
    })

@app.delete(
    "/api/v1/organisation/{org_id}/bookmark/{obj_id}/delete"
)
def delete_bookmarked_notice(org_id: str, obj_id: str):
    """This endpoint enables a user delete a bookmarked notice."""
    bookmarked_notice = db.delete(org_id, "bookmark_notice", obj_id)

    # bookmarked_data = db.read("bookmark_notice", org_id)

    # data = {
    #     "event":"delete_bookmark",
    #     "data":bookmarked_data
    # }

    # response = requests.get(f"https://noticeboard.zuri.chat/api/v1/organisation/{org_id}/get-room")
    # room = response.json()
    # room_id = room["data"][0]["_id"]

    # db.post_to_centrifugo("team-aquinas-zuri-challenge-007", data)
    # db.post_to_centrifugo("team-aquinas-zuri-challenge-007", bookmarked_data)

    if bookmarked_notice["status"] == 200:
        return JSONResponse(
            {"message": "successfully deleted bookmarked notice"},
            status_code=status.HTTP_200_OK,
        )
    return JSONResponse(
        {"message": "could not delete bookmarked notice"},
        status_code=status.HTTP_404_NOT_FOUND,
    )

@app.post(
    "/api/v1/organisation/{org_id}/create_draft",
    tags=["Notices"],
    summary="Draft Of A Notice",
)
def notice_draft(org_id: str, draft: NoticeDraft):
    """For creating Drafts for A Notice."""
    serializer = draft.dict()
    if serializer.is_valid():
        db.save("noticeboard", org_id, notice_data=serializer)
        return JSONResponse({
            "success":True,
            "data":serializer,
            "message":"successfully drafted"
        },
        status_code=status.HTTP_201_CREATED)

    return JSONResponse({
        "success":False,
        "message":"could not be drafted"
    }, 
    status_code=status.HTTP_400_BAD_REQUEST)
